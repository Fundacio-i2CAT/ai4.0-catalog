"""
Module for use as proxy to the Eurecat authentication service.
"""

import sys
import json
import os
import logging
from urllib import quote_plus
from requests import get, put, post, delete, Session

from anella.utils import load_config
from anella.common import *
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

LOGGER = logging.getLogger('stdout')

class Authenticator(object):

    def __init__(self):
       self.root_path='http://%s:%s/LmpApiI2cat/' % (get_cfg('auth__host'), get_cfg('auth__port'))
       self.session = Session()
       # For debugging purposes
       self.r_data = None
       self.path = None

    def user_login(self, email, password):
        path = self.root_path + 'loginWithPassword?email=' + email + '&password=' + password
        req = self.session.get(path)
        token = self.verify_auth_token('eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ4MTEzMDE0MywiaWF0IjoxNDgxMTI5ODQzfQ.eyJpZCI6IjI1In0.m8wAxNP36N39WFR65at7w4qXVsJIr8-kyGXAgmvjiYI')
        #token = self.generate_auth_token()
        print token
        return req.status_code

        

    def user_find(self, user):
        self.path = self.root_path+'people/search/findFirstByEmail?email='+quote_plus(user.email)
        self.req = self.session.get(self.path)
        if self.req.status_code==200:
            return json.loads(self.req.text)


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

    def user_create(self, item):
        req = self.session.post(self.root_path + 'people', json=item)
        data = json.loads(req.text)
        return {'code': req.status_code, 'message': data['cause']['cause']['message']}
   
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

    def generate_auth_token(self, expiration=300):
        s = Serializer('secret-key', expires_in=expiration)
        return s.dumps({'id': '25'})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer('secret-key')
        try:
            data = s.loads(token)
        except SignatureExpired:
            print 'entar aqui'
            return None  # valid token, but expired
        except BadSignature:
            print 'aquiiiii'
            return None  # invalid token
        print data
        return "ok"


