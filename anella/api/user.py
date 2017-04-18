# -*- coding: utf-8 -*-

from anella.common import get_db, get_arg
from anella.model.user import User
from anella.api.utils import ColRes, ItemRes, item_to_json, respond_json, \
    get_json, get_int, count_collection, find_one_in_collection, create_message_error, create_response
from anella.api.service_manager_mailer import ServiceManagerMailer
from anella import configuration as _cfg
import json
from anella.security.authorize import get_exists_user
from anella.api.keystone import Keystone
from requests import Session
from bson.objectid import ObjectId


def get_num_page(page):
    _page = 0
    if page is not None:
        _page = int(page) - 1
    return str(_page)


def jsonDefault(object):
    return object.__dict__

class UsersCrudRes(ColRes):
    def __init__(self):
        self.collection = 'users'
        self.filter = {"_cls": {"$in": ['User.Client', 'User.Provider']}}
        self.fields = "_id,_cls,user_name,activated,name,surname,email,company,address,phone,position," \
                      "legal,identification".split(",")

    @get_exists_user('User.Administrator')
    def get(self):
        limit = get_int(get_arg('limit'))
        skip = get_int(get_arg('skip'))
        result = super(UsersCrudRes, self)._get_items(skip=skip * limit, limit=limit, values=self.filter)
        response = dict(count=count_collection(self.collection, self.filter), skip=skip, limit=limit,
                        result=result)
        return respond_json(response, status=200)

class UserCrudRes(ColRes):
    def __init__(self):
        self.session = Session()
        self.keystone = Keystone()
        self.collection = 'users'
        self.smm = ServiceManagerMailer()
        self.u = User()

    @get_exists_user('User.Administrator')
    def put(self, id):
        data = get_json()
        user = find_one_in_collection(self.collection, {"_id": ObjectId(id)})
        response = self.keystone.patch_user(user['keystone_user_id'], data['activated'])
        if response.status_code == 200:
            item = json.loads(response.text)
            if user['activated'] and not data['activated']:
                self.smm.ban(data['email'])
            if data['activated'] and not user['activated']:
                self.smm.welcome(data['email'])
            if '_id' in data:
                del data['_id']
            try:
                self.u.update(id, data)
            except Exception as e:
                print e
                response.status_code = 400
                item = create_message_error(400, "USER_NOT_FOUND")
                self.keystone.patch_user(user['keystone_user_id'], not (data['activated']))
        else:
            item = create_message_error(response.status_code, "USER_NOT_FOUND")
        return create_response(response.status_code, item)

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
        self.update_user_status(self, id, False)
        return get_response(req)

    def update_user_status(self, id, status):
        u = User()
        data = {'auth_id': int(id), 'info': {'$set': {'activated': status}}}
        u.update(data)

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
