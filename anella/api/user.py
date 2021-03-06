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
        self.filter = {"_cls": {"$in": ['User.Client', 'User.Provider']}, "deleted": False}
        self.fields = "_id,_cls,user_name,activated,name,surname,email,company,address,phone,position," \
                      "legal,identification".split(",")

    @get_exists_user('User.Administrator')
    def get(self):
        limit = get_int(get_arg('limit'))
        skip = get_int(get_arg('skip'))
        items = super(UsersCrudRes, self)._get_items(skip=skip * limit, limit=limit, values=self.filter)
        result = self._items_to_json(items)
        response = dict(count=count_collection(self.collection, self.filter), skip=skip, limit=limit,
                        result=result)
        return respond_json(response, status=200)

class UserCrudRes(ColRes):
    def __init__(self):
        self.keystone = Keystone()
        self.collection = 'users'
        self.smm = ServiceManagerMailer()
        self.u = User()
        self.fields = "_id,_cls,user_name,activated,name,surname,email,company,address,phone,position," \
                      "legal,identification".split(",")
        self.item = None
        self.data_delete = {'activated': False, "deleted": True}

    @get_exists_user('User.Administrator')
    def put(self, id):
        data = get_json()
        user = find_one_in_collection(self.collection, {"_id": ObjectId(id)})
        if 'activated' in data:
            response = self.keystone.patch_user(user['keystone_user_id'], data['activated'])
            if response.status_code == 200:
                if user['activated'] and not data['activated']:
                    self.smm.ban(user['email'])
                if data['activated'] and not user['activated']:
                    self.smm.welcome(user['email'])
        if '_id' in data:
            del data['_id']
        try:
            self.u.update(id, data)
            status_code = 204
        except Exception as e:
            print e
            status_code = 400
            self.item = create_message_error(status_code, "USER_NOT_FOUND")
            if 'activated' in data:
                self.keystone.patch_user(user['keystone_user_id'], not (data['activated']))
        return create_response(status_code, self.item)

    @get_exists_user('User.Administrator')
    def patch(self, id):
        return self.put(id)

    @get_exists_user('User.Administrator')
    def delete(self, id):
        self.u.update(id, self.data_delete)
        user = self.u.get(id)
        response = self.keystone.patch_user(user['keystone_user_id'], False)
        if response.status_code == 200:
            status_code = 204
            item = None
        else:
            status_code = 404
            item = create_message_error(404, "USER_NOT_FOUND")
        return create_response(status_code, item)

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
