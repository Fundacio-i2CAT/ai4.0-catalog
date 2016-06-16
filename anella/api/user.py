# -*- coding: utf-8 -*-

import json
import os
import time

from flask_restful import reqparse, abort, Resource

from anella.common import *
from anella.model.user import User

from anella.api.utils import ColRes, ItemRes

class UsersRes(ColRes):
    collection= 'users'
    _cls = User
    name= 'Users'
    fields = '_id,email,user_name,first_name,last_name,partner_id,created_at,updated_at'.split(',')
    filter_fields = 'email,user_name,partner_id'.split(',')

    
class UserRes(ItemRes):
    collection= 'users'
    _cls = User
    name= 'User'
    fields = '_id,email,user_name,first_name,last_name,partner_id,created_at,updated_at'.split(',')

