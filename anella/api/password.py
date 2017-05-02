from anella.api.utils import ColRes, ItemRes, create_response, create_message_error, get_json
from anella.api.service_manager_mailer import ServiceManagerMailer
import random, string
from anella.api.keystone import Keystone
import json
from anella.model.user import User
from anella.security.authorize import get_exists_user, get_authorize


def generate_password():
    rand_str = lambda n: ''.join([random.choice(string.lowercase) for i in xrange(n)])
    return rand_str(15)


class PasswordRes(ColRes):
    def __init__(self):
        self.smm = ServiceManagerMailer()
        self.collection = 'users'
        self.fields = 'user_name,email,keystone_user_id,activated'.split(",")
        self.keystone = Keystone()
        self.item = None
        self.status_code = 204
        self.u = User()

    def post(self):
        data = get_json()
        user = self.u.get_by_field('email', data['email'])
        if user is None:
            self.item = create_message_error(404, '')
            return create_response(404, self.item)
        new_password = generate_password()
        response = self.keystone.patch_user(user['keystone_user_id'], new_password)
        if response.status_code == 200:
            self.smm.change_password(user['email'], new_password)
            self.u.update(str(user['_id']), {"password": True})
        else:
            self.status_code = response.status_code
            self.item = create_message_error(self.status_code, json.loads(response.text))

        return create_response(self.status_code, self.item)

class Password(ItemRes):
    def __init__(self):
        self.smm = ServiceManagerMailer()
        self.collection = 'users'
        self.fields = 'user_name,email,keystone_user_id,activated'.split(",")
        self.keystone = Keystone()
        self.item = None
        self.status_code = 204
        self.u = User()

    def get(self, id):
        user = self.get_user(id)
        if user is None: return create_response(404,
                                                create_message_error(404,
                                                                     'USER_NOT_ACTIVATED'))
        new_password = generate_password()
        response = self.keystone.patch_user(user['keystone_user_id'], new_password)
        if response.status_code == 200:
            self.smm.change_password(user['email'], new_password)
            self.u.update(id, {"password": True})
        else:
            self.status_code = response.status_code
            self.item = create_message_error(self.status_code, json.loads(response.text))

        return create_response(self.status_code, self.item)

    @get_exists_user(None)
    @get_authorize(None, 'users', False, '_id', True)
    def put(self, id):
        data = get_json()
        user = self.get_user(id)
        if user is None: return create_response(404,
                                                create_message_error(404,
                                                                     'USER_NOT_ACTIVATED'))
        response = self.keystone.change_password(user['keystone_user_id'], data)
        if response.status_code is not 204:
            self.status_code = response.status_code
            self.item = create_message_error(self.status_code, json.loads(response.text))
        else:
            self.u.update(id, {"password": False})
        return create_response(self.status_code, self.item)

    def get_user(self, id):
        user = super(Password, self).get(id)
        if not user['activated']: return None
        return user
