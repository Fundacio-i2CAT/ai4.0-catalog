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

        if self.req.status_code in (200,201):
            data = json.loads(self.req.text)
            id = data['service_instance_id']
            return id
    
    def instance_get_state(self, id):
        # import pdb;pdb.set_trace()
        if self.is_fake:
            return randint(0,2)
 
        self.path = self.root_path+'/%s' % id
        self.req = get(self.path)
        if self.debug:
            print_resp(self.req)

        if self.req.status_code in (200,201):
            data = json.loads(self.req.text)
            state = data['state']
            return state
 
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

        return bool(self.req.status_code == 200)
 
    def instance_delete(self,id):
        self.path = self.root_path+'/%s' % id
        self.req = delete(self.path)
        if self.debug:
            print_resp(self.req)

        return bool(self.req.status_code == 204)


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
