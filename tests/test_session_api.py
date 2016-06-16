# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
import urllib
from time import sleep

from flask import json, jsonify

from app import AppTestCase

__all__ = ('SessionApiTest', )

class SessionApiTest(AppTestCase):

    def test_session_get(self):
        self.create_admin()
        self.create_user()

        sleep(1)
        data = { "email" : self.admin.email, "password": self.admin.user_name }
        resp = self.app.post('/api/session', data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 200)

        resp = self.app.get(u'/api/session')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['email'], 'oscar.rambla@i2cat.net')

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


if __name__ == '__main__':
    unittest.main()
