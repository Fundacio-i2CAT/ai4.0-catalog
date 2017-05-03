#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Plataforma Industrial 4.0 Service Manager Tests"""

import json
import unittest
import requests
import random
import time
import uuid
import sys
import os

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
BASE_URL = 'http://dev.anella.i2cat.net:9999'

CLIENT_REGISTER_FORM = {
    'name': '',
    'surname': '',
    'email': '',
    'company': 'i2CAT',
    'comp_address': 'Nexus II',
    'comp_phone': '55555555555',
    'comp_position': 'Developer',
    'client_role': False,
    'provider_role': True,
    'legal': False,
    'password': 'i2cat',
    'identification_number':
    {
        'isnif': True,
        'value': None
    }
}

def nif_generator():
    number = random.randint(10**(8-1), (10**8)-1)
    letters = ['T', 'R', 'W', 'A', 'G', 'M', 'Y', 'F',
               'P', 'D', 'X', 'B', 'N', 'J', 'Z', 'S',
               'Q', 'V', 'H', 'L', 'C', 'K', 'E']
    return str(number)+letters[number % 23]

def register(email, password, provider=False):
    """Register function"""
    CLIENT_REGISTER_FORM['name'] = email
    CLIENT_REGISTER_FORM['user_name'] = email
    CLIENT_REGISTER_FORM['surname'] = email
    CLIENT_REGISTER_FORM['email'] = email
    CLIENT_REGISTER_FORM['password'] = password
    if provider:
        CLIENT_REGISTER_FORM['client_role'] = False
        CLIENT_REGISTER_FORM['provider_role'] = True
    else:
        CLIENT_REGISTER_FORM['client_role'] = True
        CLIENT_REGISTER_FORM['provider_role'] = False
    CLIENT_REGISTER_FORM['identification_number']['value'] = nif_generator()
    print CLIENT_REGISTER_FORM
    resp = requests.post('{0}/api/register'.format(BASE_URL),
                         headers={'Content-Type': 'application/json'},
                         json=CLIENT_REGISTER_FORM)
    print resp.status_code
    assert resp.status_code == 204

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print 'Usage: python {0} email password [provider]'.format(sys.argv[0])
        exit(0)

    email = sys.argv[1]
    password = sys.argv[2]
    print email, password
    
    if len(sys.argv) == 4:
        register(email, password, True)
    else:
        register(email, password)
    
        
