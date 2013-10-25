import webapp2
import json
from mako.template import Template
from mako.lookup import TemplateLookup
from webapp2_extras import mako
from datetime import datetime
from services import people as people_service

import logging

log = logging.getLogger(__name__)

mako.default_config.update(dict(
	    input_encoding='utf-8',
	    output_encoding = 'utf-8',
	    default_filters=['decode.utf8']
    ))

class BaseHandler(webapp2.RequestHandler):
    """BaseHandler which will be inherited all other handlers 
    it should implement the most common functionality
    required by all handlers 
    """

    def __init__(self, request, response):
	self.initialize(request, response)
        self._handle_login(request)

    def _handle_login(self, request):
        cc_user = None
        user_session_info = request.cookies.get(self.app.config.get('SESSION_COOKIE_NAME'))
        log.info('user_session_info: %s' % user_session_info)
        if user_session_info:
            try:
                uid = int(user_session_info.split("x")[1])
                session_start_time = datetime.strptime(user_session_info.split("x")[0], '%Y%m%d')
                cc_user = people_service.get_person_by_id(uid)
                log.info('Logged in user %s' % cc_user.first_name)
            except:
                log.exception('Non-logged in user')
        self.app.cc_user = cc_user


    @webapp2.cached_property
    def mako(self):
	return mako.get_mako(app=self.app)

    def render_response(self, _template, **context):
	context['config'] = self.app.config
	context['request'] = self.request
	context['template_name'] = _template
	context['cc_user'] = self.app.cc_user.to_dict() if self.app.cc_user is not None else None
	rv = self.mako.render_template(_template, **context)
	self.response.write(rv)

    def render_json(self, obj):
	rv = json.dumps(obj) 
	self.response.headers.content_type = 'application/json'
	self.response.write(rv)

    def authenticate(self, response_type = 'page'):
        #return True
        if self.app.cc_user:
	    return True
	else:
	    if response_type == 'page':
		self.render_response('login.html', next_url = self.request.url)
	    else:
		self.render_json({'success': False, 'message': 'Login Failure'})
	    return False
