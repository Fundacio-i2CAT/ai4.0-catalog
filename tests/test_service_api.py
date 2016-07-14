# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
from time import sleep

from flask import json, jsonify

from app import AppTestCase

__all__ = ('ServiceApiTest', )

class ServiceApiTest(AppTestCase):

    def test_empty_get(self):
        resp = self.app.get('/api/services')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 0)
        self.assertEqual( data['status'], 'ok')

    def test_services_get(self):
        self.create_admin()
        self.create_provider()
        self.create_generic()
        self.create_cloud()
        sleep(1)

        resp = self.app.get(u'/api/services')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 2)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get('/api/services?name=cloud_service2')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 1)

    def test_services_post(self):
        self.create_admin()
        self.create_provider()
        sleep(1)

        data = { "name" : "cloud_service3", 
                 "provider" : unicode(self.provider.pk), 
                 "keywords" : [ "storage" ], "sectors" : [ "industry" ], 
                 "service_type" : "iss" }
        resp = self.app.post('/api/services', data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')
        self.assertIsNotNone( data['id'])

        service_id = data['id']

        resp = self.app.get(u'/api/services/'+service_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['service_type'], 'iss')


    def test_service_get(self):
        self.create_admin()
        self.create_provider()
        self.create_generic()

        service_id = unicode(self.generic.pk)

        sleep(1)
        resp = self.app.get(u'/api/services/'+service_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['service_type'], 'app')

    def test_service_delete(self):
        self.create_admin()
        self.create_provider()
        self.create_generic()

        service_id = unicode(self.generic.pk)

        sleep(1)
        resp = self.app.delete('/api/services/'+service_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get(u'/api/services/'+service_id)
        self.assertEqual( resp.status_code, 404)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'fail')


    def test_service_put(self):
        self.create_admin()
        self.create_provider()
        self.create_cloud()

        service_id = unicode(self.cloud.pk)

        sleep(1)
        data = '''{ "name" : "cloud_service3", "provider" : "575062ee76e63a35bede35d3", "keywords" : [ "storage" ], "sectors" : [ "industry" ], "service_type" : "iss" }''' 
        resp = self.app.put('/api/services/'+service_id, data=data, 
                            content_type='application/json')

        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get(u'/api/services/'+service_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['service_type'], 'iss')

if __name__ == '__main__':
    unittest.main()
