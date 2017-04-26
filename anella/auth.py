"""
Module for use as proxy to the Eurecat authentication service.
"""
import json
import logging
from requests import Session
from anella.model.user import UserRole, Administrator, Client, Provider
from anella.api.utils import create_response, find_one_in_collection, \
    create_message_error
import jwt
from datetime import datetime, timedelta
from anella.api.keystone import Keystone
from anella.model.token import Token

LOGGER = logging.getLogger('stdout')

cls_dict = {
    "administrator": Administrator,
    "client": Client,
    "provider": Provider
}


class Authenticator(object):
    def __init__(self):
        self.session = Session()
        self.user = None
        self.item = create_message_error(401, "USER_NOT_ACTIVATED")
        self.keystone = Keystone()
        self.time_token = Token().get()

    def user_login(self, email, password):
        self.keystone.keystone_admin = email
        self.keystone.keystone_admin_pass = password
        response = self.keystone.get_login()

        if response.status_code == 201:
            # Encontrado el usuario en Keystone. Lo buscamos en mongo
            data = find_one_in_collection('users',
                                          {'keystone_user_id': json.loads(response.text)['token']['user']['id']})
            if data is not None:
                self.create_role_user(data)
                response.status_code = 200
            else:
                response.status_code = 404
                self.item = create_message_error(response.status_code, "USER_NOT_FOUND")
        return create_response(response.status_code, self.item)

    def create_role_user(self, data):
        self.user = UserRole()
        self.item = self.user.__dict__
        self.user.user_name = data['name']
        self.user.id = str(data['_id'])
        self.user.role = data['_cls']
        self.user.password = data['password']
        self.create_token()

    def create_token(self):
        payload = {
            'user_id': self.user.id,
            'exp': datetime.utcnow() + timedelta(seconds=self.time_token),
            'role': self.user.role
        }
        jwt_token = jwt.encode(payload, 'secret', 'HS256')
        self.user.token = jwt_token
