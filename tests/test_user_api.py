# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
import urllib
from time import sleep

from flask import json, jsonify

from app import AppTestCase

__all__ = ('UserApiTest', )

class UserApiTest(AppTestCase):

    def test_empty_get(self):
        resp = self.app.get('/api/users')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 0)
        self.assertEqual( data['status'], 'ok')

    def test_users_get(self):
        self.create_admin()
        self.create_user()
        sleep(1)

        resp = self.app.get(u'/api/users')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 2)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get('/api/users?user_name=user.prov')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['count'], 1)

#         resp = self.app.get(urllib.quote_plus('/api/users?email=user.prov@prov1.com'))
        resp = self.app.get('/api/users?email=user.prov@prov1.com')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['count'], 1)

    def test_users_post(self):
        self.create_admin()
        self.create_provider()
        partner_id = unicode(self.provider.pk)
        sleep(1)

        data = { "email" : "user3.prov1@prov1.com", "password" : self.admin.user_name,
                 "partner_id": partner_id }
        resp = self.app.post('/api/users', data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')
        self.assertIsNotNone( data['id'])

        user_id = data['id']

        resp = self.app.get(u'/api/users/'+user_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['email'], 'user3.prov1@prov1.com')


    def test_user_get(self):
        self.create_admin()
        self.create_user()
        user_id = unicode(self.user.pk)

        sleep(1)
        resp = self.app.get(u'/api/users/'+user_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['email'], 'user.prov@prov1.com')

    def test_signin(self):
        self.create_admin()
        user_id = unicode(self.admin.pk)

        sleep(1)
        data = { "email" : self.admin.email, "password": self.admin.user_name }
        resp = self.app.post('/api/session', data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 200)

        data = { "user_name" : self.admin.user_name, "password": self.admin.user_name }
        resp = self.app.post('/api/session', data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 200)

        data = { "user_name" : self.admin.user_name, "password": 'aaa' }
        resp = self.app.post('/api/session', data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 400)

    def test_signout(self):
        self.create_admin()
        user_id = unicode(self.admin.pk)
        sleep(1)
        data = { "email" : self.admin.email, "password": self.admin.user_name }
        resp = self.app.post('/api/session', data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 200)

        resp = self.app.delete('/api/session')
        self.assertEqual( resp.status_code, 200)

        resp = self.app.delete('/api/session')
        self.assertEqual( resp.status_code, 400)


    def _test_user_delete(self):
        self.create_admin()
        self.create_user()

        user_id = unicode(self.user.pk)

        sleep(1)
        resp = self.app.delete('/api/users/'+user_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get(u'/api/users/'+user_id)
        self.assertEqual( resp.status_code, 404)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'fail')


    def _test_user_put(self):
        self.create_admin()
        self.create_user()

        user_id = unicode(self.user.pk)

        sleep(1)
        data = '''{ "name" : "user3", "sectors" : [ "industry" ], "contact": { "email": "prov3@prov3.com" } }''' 
        resp = self.app.put('/api/users/'+user_id, data=data, 
                            content_type='application/json')

        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get(u'/api/users/'+user_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['contact']['email'], 'prov3@prov3.com')

if __name__ == '__main__':
    unittest.main()
