# -*- coding: utf-8 -*-

from anella.common import get_db, get_cfg
from anella.model.user import User
from anella.api.utils import ColRes, ItemRes, item_to_json, respond_json, get_json, get_arg
from anella import configuration as _cfg
from requests import Session
import json
from anella.security.authorize import get_exists_user


def get_num_page(page):
    _page = 0
    if page is not None:
        _page = int(page) - 1
    return str(_page)


class UsersCrudRes(ColRes):
    def __init__(self):
        self.root_path='https://%s:%s/1.0/LmpApiI2cat/people/' % (get_cfg('auth__host'), get_cfg('auth__port'))
        self.session = Session()
        with open(get_cfg('auth__oauth')) as fhandle:
            self.authorization = json.load(fhandle)
        self.session.headers.update(self.authorization['headers'])
        # Waiting for Eurecat's certificate ...
        #    meanwhile verification disabled
        self.session.verify = False

    @get_exists_user('User.Administrator')
    def get(self):
        page = get_arg('page')
        path = self.root_path + '?page=' + get_num_page(page)
        req = self.session.get(path)
        return get_response(req)


class UserCrudRes(ColRes):
    def __init__(self):
        self.root_path = '%s%s' % (_cfg.auth__eurecat, 'people/')
        self.session = Session()
        with open(_cfg.auth__oauth) as fhandle:
            self.authorization = json.load(fhandle)
        self.session.headers.update(self.authorization['headers'])
        # Waiting for Eurecat's certificate ...
        #    meanwhile verification disabled
        self.session.verify = False

    @get_exists_user('User.Administrator')
    def put(self, id):
        data = get_json()
        path = self.root_path + id
        # PROVISIONAL CAMBIAMOS POR PATCH
        req = self.session.patch(path, headers={'Content-Type': 'application/json'}, json=data)
        return get_response(req)

    @get_exists_user('User.Administrator')
    def patch(self, id):
        data = get_json()
        path = self.root_path + id
        req = self.session.patch(path, headers={'Content-Type': 'application/json'}, json=data)
        return get_response(req)

    @get_exists_user('User.Administrator')
    def delete(self, id):
        data = get_json()
        path = self.root_path + id
        req = self.session.patch(path, headers={'Content-Type': 'application/json'}, json=data)
        user = User()
        item = dict(auth_id=int(id), info={'$set': {"activated": False}})
        user.update(item)
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
