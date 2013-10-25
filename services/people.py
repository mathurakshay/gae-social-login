from models.people import People
from datetime import datetime

import logging

log = logging.getLogger(__name__)


def get_person_by_id(uid):
    return People.get_by_id(int(uid))


def authenticate_person(person, password):
    return person if person and person.passwd == _get_password_hash(password) else None

def get_person_by_email(email_addr):
    person_list = People.gql("where email_addr = :1", email_addr)
    try:
        person = person_list[0]
    except:
        person = None

    return person

def get_fb_user(fb_uid):
    person_list = People.gql("where fb_uid = :1", fb_uid)
    try:
        person = person_list[0]
    except:
        person = None

    return person

def get_people(query_str):
    return [p.to_dict() for p in People.gql(query_str)]

def create_person(**kwargs):
    person = People(**kwargs)
    person.passwd = _get_password_hash(person.passwd)
    person.createdon = datetime.utcnow()
    person.last_login = datetime.utcnow()
    person.put()

    return person

def update_person_info(id, **person_info):
    old_person = People.get_by_id(int(id))
    person = old_person.update(person_info)
    person.put()

    return person


    
def _get_password_hash(password_string):
    import hashlib

    return hashlib.sha256(password_string).hexdigest() if password_string else None

