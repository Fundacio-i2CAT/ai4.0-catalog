"""
Module for use as proxy to the Eurecat authentication service.
"""
import json
import logging
from urllib import quote_plus
from requests import Session

from anella.common import *
from anella.model.user import UserRole, User, Administrator, Client, Provider
from anella.api.utils import create_response

LOGGER = logging.getLogger('stdout')


cls_dict = {
    "administrator": Administrator,
    "client": Client,
    "provider": Provider
}

class Authenticator(object):

    def __init__(self):
        self.root_path='https://%s:%s/LmpApiI2cat/1.0' % (get_cfg('auth__host'), get_cfg('auth__port'))
        self.session = Session()
        with open(get_cfg('auth__oauth')) as fhandle:
            self.authorization = json.load(fhandle)
        self.session.headers.update(self.authorization['headers'])
        # Waiting for Eurecat's certificate ...
        #    meanwhile verification disabled
        self.session.verify = False
        # For debugging purposes
        self.r_data = None
        self.path = None
        self.user = None
        self.item = dict(message="User not found")
        self.provider = None

    def user_login(self, email, password):
        path = self.root_path + 'authenticateWithPassword?email=' + email + '&password=' + password
        req = self.session.get(path)

        if req.status_code == 200:
            #Encontrado el usuario
            self.create_role_user()
            self.user.email = email
            data = self.user_find(self.user)
            self.user.user_name = data['name']
            self.user.auth_id = data['id']
            self.provider = data['providerRole']
            try:
                self.user.role = self.find_user_role(data['_links']['associations']['href'])
                self.user.id = self.get_cls()
            except IndexError:
                req.status_code = 500
                self.item = dict(message="This user isn't associated any entity")
        return create_response(req.status_code, self.item)

    def create_role_user(self):
        self.user = UserRole()
        self.item = self.user.__dict__

    def user_find(self, user):
        self.path = self.root_path+'people/search/findFirstByEmail?email='+quote_plus(user.email)
        self.req = self.session.get(self.path)
        if self.req.status_code==200:
            return json.loads(self.req.text)

    def find_user_role(self, url):
        req = self.session.get(url)
        data = json.loads(req.text)
        self.find_entity_user(data['_embedded']['personEntityRelationships'][0]['_links']['organization']['href'])
        return data['_embedded']['personEntityRelationships'][0]['state']

    def find_entity_user(self, url):
        req = self.session.get(url)
        data = json.loads(req.text)
        self.user.entity = data['identifier']

    def user_get(self, id):
        self.path = self.root_path+'people/'+str(id)
        self.req = self.session.get(self.path)
        if self.req.status_code==200:
            return json.loads(self.req.text)

    def user_auth(self, user, password):
        if user.auth_id:
            auth = self.user_get(user.auth_id)
        else:
            auth = self.user_find(user)
        if auth:
            return auth['password']==password
        else:
            LOGGER.debug("User '%s' not found." % user.user_name)

    def user_create(self, user, password):
        # import pdb;pdb.set_trace()
        auth = self.user_find(user)
        if auth:
            user.auth_id = auth['id']
            user.save()
            return

        self.path = self.root_path+'people'
        self.r_data = dict(name=user.first_name, surname=user.last_name,
                     email=user.email, password=password,
                     identifier=user.nif,
                     phone=user.phone_number )

        self.req = self.session.post(self.path, json=self.r_data)
        if self.req.status_code==201:
            auth_id= json.loads(self.req.text)['id']
            user.auth_id = auth['id']
            user.save()
            return auth_id

        return self.req.status_code==201

    def entity_find(self, partner):
        self.path = self.root_path+'entities/search/findFirstByEmail?email='+quote_plus(partner.contact.email)
        self.req = self.session.get(self.path)
        return self.req.status_code == 200

    def entity_create(self, partner):
        if self.entity_find(partner):
            return

        self.path = self.root_path+'entities'
        self.r_data = dict(name=partner.name, email=partner.contact.email, identifier=partner.nif)

        self.req = self.session.post(self.path, json=self.r_data)
        return self.req.status_code==201

    def get_cls(self):
        #Primero miramos si existe en la BBDD
        user = User()
        item = user.get(self.user.auth_id)
        if item is None:
            _class = self.get_role_user()
            admin = _class(user_name=self.user.email, auth_id=self.user.auth_id)
            admin.save()
            _id = str(str(admin.pk))
            tmp = user.get(self.user.auth_id)
            self.user.role = tmp['_cls']
        else:
            _id = str(item['_id'])
            self.user.role = item['_cls']
        return _id

    def get_role_user(self):
        _class = cls_dict['client']
        if self.user.role == 'ADMINISTRATOR':
            _class = cls_dict['administrator']
        elif self.provider:
            _class = cls_dict['provider']
        return _class
