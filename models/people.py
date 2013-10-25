from google.appengine.ext import db
from datetime import datetime


class People(db.Model):
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    email_addr = db.StringProperty()
    acq_source = db.StringProperty()

    fb_uid = db.StringProperty()
    ss_uid = db.StringProperty()
    dob = db.StringProperty()
    gender = db.StringProperty()

    createdon = db.DateTimeProperty()
    last_login = db.DateTimeProperty()

    passwd = db.StringProperty()


    def to_dict(self):
        our_dict = self.__dict__.copy()['_entity']
	our_dict['id'] = self.key().id()
	our_dict['createdon'] = self.createdon.strftime('%d %b %Y') if self.createdon else ''
	our_dict['last_login'] = self.last_login.strftime('%d %b %Y') if self.last_login else ''
        if 'passwd' in our_dict:
            del our_dict['passwd']
        return our_dict

    def update(self, new_values):
	for p in new_values:
	    self.__setattr__(p, new_values.get(p))
	return self

