"""
Module to be used as proxy with the Orchestation service.
"""

import sys
import json
import os
from random import randint
from requests import get, put, post, delete, Session
from pprint import pprint
from anella.common import *
from anella.api.utils import create_response_data

class Orchestrator(object):

    def __init__(self, debug=True, is_fake=False):
        if get_cfg('orch__host'):
            self.root_path='http://%s:%s/orchestrator/api/v0.1/service/instance' % (get_cfg('orch__host'), get_cfg('orch__port'))
            self.is_fake=is_fake
        else:
            self.is_fake=True

        self.debug=debug
 
    def instance_create(self,sproject):
        # import pdb;pdb.set_trace()
        if self.is_fake:
            return randint(1,9999)
 
        self.path = self.root_path
        # self.r_data = json.dumps(sproject)
        self.r_data = sproject
    
        self.req = post(self.path, json=self.r_data)
        if self.debug:
            print_resp(self.req, self.r_data)
        print self.req
        return self.req
    
    def instance_get_state(self, id):
        # import pdb;pdb.set_trace()
        if self.is_fake:
            return randint(0,2)
 
        self.path = self.root_path+'/%s' % id
        self.req = get(self.path)
        if self.debug:
            print_resp(self.req)

        if self.req.status_code in (200,201):
            return json.loads(self.req.text)
 
    def instance_set_state(self, id, state):
        # import pdb;pdb.set_trace()
        if self.is_fake:
            return randint(0,2)
 
        # ULL: Orch. expects /state on PUT :/
        self.path = self.root_path+'/%s/state' % id
        self.r_data = dict(state=state)
        self.req = put(self.path, json=self.r_data)
        if self.debug:
            print_resp(self.req, self.r_data)

        return dict(status_code= self.req.status_code, response=json.loads(self.req.text))
 
    def instance_delete(self,id):
        self.path = self.root_path+'/%s' % id
        self.req = delete(self.path)
        if self.debug:
            print_resp(self.req)

        return bool(self.req.status_code == 204)

    def get_flavors(self, pop_id):
        path = 'http://%s:%s/orchestrator/api/v0.1/pop/%s/flavors' % (get_cfg('orch__host'), get_cfg('orch__port'), pop_id)
        data = get(path)
        return create_response_data(data)

    def get_pop(self):
        path = 'http://%s:%s/orchestrator/api/v0.1/pop' % (get_cfg('orch__host'), get_cfg('orch__port'))
        data = get(path)
        return create_response_data(data)

    def exists(self, data):
        path = 'http://%s:%s/orchestrator/api/v0.1/iscached/%s' % (get_cfg('orch__host'), get_cfg('orch__port'), data['pop_id'])
        resp = post(path, json=data)
        return resp

def print_resp(req, data=None):
    print '%s %s %s' % (req.request.method, req.request.url, req.status_code)
    print('='*70)
    pprint(req.headers)
    print('='*70)

    if data:
#         pprint(data)
        print(json.dumps(data, indent=2))
        print('*'*70)

#     pprint(json.loads(req.text))
    if req.text:
        print(json.dumps(json.loads(req.text), indent=4))

#     print('*'*70)
