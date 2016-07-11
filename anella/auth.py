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

LOGGER = logging.getLogger('stdout')

class Authenticator(object):

   def __init__(self):
       self.root_path='http://%s:%s/LmpApi/' % (get_cfg('auth__host'), get_cfg('auth__port'))
       self.session = Session()
       # For debugging purposes
       self.r_data = None
       self.path = None

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


