# -*- coding: utf-8 -*-

from anella.common import get_db
from anella.model.user import User

from anella.api.utils import ColRes, ItemRes, item_to_json

class UsersRes(ColRes):
    collection = 'users'
    _cls = User
    name = 'Users'
    fields = '_id,email,user_name,first_name,last_name,'\
             'idiom,admin,partner,created_at,updated_at'.split(',')
    filter_fields = 'email,user_name,partner_id'.split(',')

    def _item_to_json(self, item):
        item = partner_to_json(item)
        return item_to_json(item, self.fields)
       

class UserRes(ItemRes):
    collection = 'users'
    _cls = User
    name = 'User'
    fields = '_id,email,user_name,first_name,last_name,'\
             'idiom,admin,partner,created_at,updated_at'.split(',')

    def _item_to_json(self, item):
        item = partner_to_json(item)
        return item_to_json(item, self.fields)
       
def partner_to_json(item):
    partner_id = item.pop('partner_id', None)
    if partner_id:
        partner = get_db()['partners'].find_one({'_id':partner_id})
        item['partner'] = item_to_json(partner, ['_id', '_cls', 'name'])
    else:
        item['partner'] = None

    return item

