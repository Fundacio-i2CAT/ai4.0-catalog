# -*- coding: utf-8 -*-

from anella.common import get_db
from anella.model.user import User

from anella.api.utils import ColRes, ItemRes, item_to_json, respond_json, get_json
from anella import configuration as _cfg
from requests import Session
import json

class UsersCrudRes(ColRes):
    def __init__(self):
        self.root_path = '%s%s' % (_cfg.auth__eurecat, 'people')
        self.session = Session()

    def get(self):
        req = self.session.get(self.root_path)
        return get_response(req)

class UserCrudRes(ColRes):
    def __init__(self):
        self.root_path = '%s%s' % (_cfg.auth__eurecat, 'people/')
        self.session = Session()

    def put(self, id):
        data = get_json()
        path = self.root_path + id
        req = self.session.put(path, headers={'Content-Type': 'application/json'}, json=data)
        return get_response(req)

    def patch(self, id):
        data = get_json()
        path = self.root_path + id
        req = self.session.patch(path, headers={'Content-Type': 'application/json'}, json=data)
        return get_response(req)

    def delete(self, id):
        data = get_json()
        path = self.root_path + id
        req = self.session.delete(path, headers={'Content-Type': 'application/json'}, json=data)
        return get_response(req)

class UsersRes(ColRes):
    collection = 'users'
    _cls = User
    name = 'Users'
    fields = '_id,email,user_name,first_name,last_name,phone_number,'\
             'idiom,admin,partner,created_at,updated_at'.split(',')
    filter_fields = 'email,user_name,partner_id'.split(',')

    def _item_to_json(self, item):
        item = partner_to_json(item)
        return item_to_json(item, self.fields)
       

class UserRes(ItemRes):
    collection = 'users'
    _cls = User
    name = 'User'
    fields = '_id,email,user_name,first_name,last_name,phone_number,'\
             'idiom,admin,partner,created_at,updated_at'.split(',')

    def _item_to_json(self, item):
        item = partner_to_json(item)
        return item_to_json(item, self.fields)
       
def partner_to_json(item):
    partner_id = item.pop('partner_id', None)
    if partner_id:
        partner = get_db(_cfg.database__database_name)['partners'].find_one({'_id':partner_id})
        item['partner'] = item_to_json(partner, ['_id', '_cls', 'name'])
    else:
        item['partner'] = None

    return item

def get_response(req):
    if req.status_code == 200:
        data = respond_json(json.loads(req.text), status=req.status_code)
    else:
        data = respond_json(dict(msg='nok'), status=req.status_code)
    return data