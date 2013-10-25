
import logging

log = logging.getLogger(__name__)

from base import BaseHandler 
from datetime import datetime

from services import people as people_service


class DefaultHandler(BaseHandler):
    def get(self):
	if self.authenticate(response_type = 'page'):
	    self.render_response('default.html')

class LoginHandler(BaseHandler):
    def get(self):
	config = self.app.config
        r = {'success': False, 'reason': 'no_user'}
	current_user = None
        info_to_update = {'last_login': datetime.utcnow()}

	login_type = self.request.get('login_type')
	username = self.request.get('username')
        log.info('login_type: %s' % login_type)

        current_user = people_service.get_person_by_email(username)
        if current_user:
            if login_type == 'email':
                password = self.request.get('password')
                if current_user.acq_source == 'email':
                    current_user = people_service.authenticate_person(current_user, password)
                    if not current_user:
                        r['reason'] = 'unmatched_password'
                else:
                    r['reason'] = 'other_login_type'
                    r['login_type'] = current_user.acq_source
                    current_user = None

        if login_type == 'facebook':
            fb_uid = str(self.request.get('fb_uid'))
            if current_user and current_user.acq_source == 'email' and (not current_user.fb_uid or current_user.fb_uid == 'None'):
                # merge
                r['reason'] = 'merge'
                r['uid'] = current_user.to_dict()['id']
                current_user = None
            elif current_user and current_user.fb_uid == fb_uid:
                # this is the user, let her login
                log.info('Facebook login for fb_uid=%s email=%s' % (fb_uid, username))
                pass
            else:
                # case where difefrent fb_uid is assigned to same FB user is not allowed 
                # by Facebook and is not handled here
                current_user = people_service.get_fb_user(fb_uid)
                if current_user:
                    # email address has changed
                    if current_user.acq_source == 'facebook':
                        info_to_update['email_addr'] = username
                    else:
                        current_user = None
                else:
                    # create_person
                    new_user_info = dict(
                                first_name = self.request.get('first_name'),
                                last_name = self.request.get('last_name'),
                                email_addr = self.request.get('username'),
                                acq_source = self.request.get('login_type'),

                                fb_uid = self.request.get('fb_uid'),
                                ss_uid = self.request.get('ss_uid'),
                                dob = self.request.get('dob'),
                                gender = self.request.get('gender')
                            )
                    current_user = people_service.create_person(**new_user_info)


        if current_user:
            people_service.update_person_info(current_user.to_dict()['id'], **info_to_update) 
            r = _get_success_response(current_user, config)

	self.render_json(r)

class LogoutHandler(BaseHandler):
    def get(self):
	config = self.app.config
        username = self.request.get('username')

	r = {
		'success': True,
		'cookie_name': config.get('SESSION_COOKIE_NAME'),
	    }
	self.render_json(r)

class PeopleRestHandler(BaseHandler):
    def get(self, id = None):
	"""Returns search results
	"""
	if self.authenticate(response_type = 'json'):
            q_type = self.request.get('q_field')
            q_value = self.request.get('q_value')

            query_str = "where %s = '%s'" %(q_field, q_value)
            try:
                people_data = people_service.get_people(query_str)
                r = {
                        'success': True,
                        'data': people_data,
                        'count': len(people_data),
                        'query': query_str
                    }
            except Exception, e:
                log.exception('error in getting data for query: %s' % query_str)
                r = {'success': False,'reason': e}
            finally:
                self.render_json(r)


    def put(self, id = 'add'):
	"""Add new person
	"""
	config = self.app.config
        person_info = {
                'acq_source' : self.request.get('acq_source'),
                'email_addr' : self.request.get('username'),
                'passwd' : self.request.get('password'),
                'first_name' : self.request.get('first_name'),
                'last_name' : self.request.get('last_name')
            }
        try:
            current_user = people_service.get_person_by_email(person_info['email_addr'])
            if current_user:
                ret = {
                        'success': False,
                        'reason': 'already_exist',
                        'login_type': current_user.acq_source
                    }
            else:
                person = people_service.create_person(**person_info)
                ret = _get_success_response(person, config)

        except Exception, e:
            log.exception('error in updating...')
            ret = {'status': False, "reason": "failure because %s" % e}
        self.render_json(ret)

    def post(self, id):
        '''
            updates a person
        '''
	config = self.app.config
        person_info = dict(
                    first_name = self.request.get('first_name'),
                    last_name = self.request.get('last_name'),
                    email_addr = self.request.get('username'),
                    acq_source = self.request.get('login_type'),

                    fb_uid = self.request.get('fb_uid'),
                    ss_uid = self.request.get('ss_uid'),
                    dob = self.request.get('dob'),
                    gender = self.request.get('gender')
                )
        try:
            current_user = people_service.get_person_by_id(id)
            password = self.request.get('password')
            current_user = people_service.authenticate_person(current_user, password)
            if current_user:
                current_user = people_service.update_person_info(id, **person_info)
                ret = _get_success_response(current_user, config)
            else:
                ret = {'status': False, "reason": "unmatched_password"}
        except Exception, e:
            log.exception('Error in merging person info %s' % person_info)
            ret = {'status': False, "reason": "failure because %s" % e}

        self.render_json(ret)


def _get_success_response(current_user, config):
    user_dict = current_user.to_dict()
    session_cookie_val = '%sx%s' % (datetime.utcnow().strftime('%Y%m%d'), user_dict['id'])
    ret = {
            'success': True,
            'uid': user_dict['id'],
            'cookie_name': config.get('SESSION_COOKIE_NAME'),
            'cookie_value': session_cookie_val
        }
    return ret