"""
Module for use as proxy to the Eurecat authentication service.
"""
import json
import logging
from urllib import quote_plus
from requests import Session

from anella.common import *
from anella.model.user import UserRole
from anella.api.utils import create_response

LOGGER = logging.getLogger('stdout')


class Authenticator(object):

    def __init__(self):
        self.root_path='http://%s:%s/LmpApiI2cat/' % (get_cfg('auth__host'), get_cfg('auth__port'))
        self.session = Session()
        # For debugging purposes
        self.r_data = None
        self.path = None
        self.user = None
        self.item = dict(message="User not found")

    def user_login(self, email, password):
        path = self.root_path + 'authenticateWithPassword?email=' + email + '&password=' + password
        req = self.session.get(path)

        if req.status_code == 200:
            #Encontrado el usuario
            self.create_role_user()
            self.user.email = email
            data = self.user_find(self.user)
            self.user.user_name = data['name']
            self.user.id = data['id']
            self.user.provider = data['providerRole']
            self.user.client = data['clientRole']
            try:
                self.user.role = self.find_user_role(data['_links']['associations']['href'])
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


