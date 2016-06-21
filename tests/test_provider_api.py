# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
from time import sleep

from flask import json, jsonify

from app import AppTestCase

__all__ = ('ProviderApiTest', )

class ProviderApiTest(AppTestCase):

    def test_empty_get(self):
        resp = self.app.get('/api/providers')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 0)
        self.assertEqual( data['status'], 'ok')

    def test_providers_get(self):
        self.create_admin()
        self.create_provider()
        sleep(1)

        resp = self.app.get(u'/api/providers')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 1)
        self.assertEqual( data['status'], 'ok')

    def test_providers_query(self):
        self.create_admin()
        self.create_provider()
        sleep(1)

        resp = self.app.get('/api/providers?name=prov1')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['count'], 1)

        resp = self.app.get('/api/providers?pip=prov1')
        self.assertEqual( resp.status_code, 400)

        resp = self.app.get('/api/providers?sectors=health')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['count'], 1)


    def test_providers_post(self):
        self.create_admin()
        sleep(1)

        data = '''{ "name" : "provider3", "sectors" : [ "industry" ], "contact": { "email": "prov3@prov3.com" } }''' 
        resp = self.app.post('/api/providers', data=data, content_type = 'application/json')
        self.assertEqual( resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')
        self.assertIsNotNone( data['id'])

        provider_id = data['id']

        resp = self.app.get(u'/api/providers/'+provider_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['contact']['email'], 'prov3@prov3.com')


    def test_provider_get(self):
        self.create_admin()
        self.create_provider()

        provider_id = unicode(self.provider.pk)

        sleep(1)
        resp = self.app.get(u'/api/providers/'+provider_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['contact']['email'], 'prov1@prov1.com')

    def test_provider_delete(self):
        self.create_admin()
        self.create_provider()

        provider_id = unicode(self.provider.pk)

        sleep(1)
        resp = self.app.delete('/api/providers/'+provider_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get(u'/api/providers/'+provider_id)
        self.assertEqual( resp.status_code, 404)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'fail')


    def test_provider_put(self):
        self.create_admin()
        self.create_provider()

        provider_id = unicode(self.provider.pk)

        sleep(1)
        data = '''{ "name" : "provider3", "sectors" : [ "industry" ], "contact": { "email": "prov3@prov3.com" } }''' 
        resp = self.app.put('/api/providers/'+provider_id, data=data, 
                            content_type='application/json')

        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get(u'/api/providers/'+provider_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['contact']['email'], 'prov3@prov3.com')

if __name__ == '__main__':
    unittest.main()
