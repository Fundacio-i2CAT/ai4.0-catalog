# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
from time import sleep

from flask import json, jsonify

from app import AppTestCase

from anella.model.partner import ANELLA_SECTORS

__all__ = ('ClientApiTest', )

class ClientApiTest(AppTestCase):

    def test_empty_get(self):
        resp = self.app.get('/api/clients')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 0)
        self.assertEqual( data['status'], 'ok')

    def test_clients_get(self):
        self.create_admin()
        self.create_client()
        sleep(1)

        resp = self.app.get(u'/api/clients')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 1)
        self.assertEqual( data['status'], 'ok')

    def test_clients_query(self):
        self.create_admin()
        self.create_client()
        sleep(1)

        resp = self.app.get('/api/clients?name=client1')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['count'], 1)

        resp = self.app.get('/api/clients?na=client1')
        self.assertEqual( resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'fail')

        resp = self.app.get('/api/clients?sectors=health')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['count'], 1)


    def test_clients_post(self):
        self.create_admin()
        sleep(1)

        data = '''{ "name" : "client3", "sectors" : [ "industry" ], "contact": { "email": "client3@client3.com" } }''' 
        resp = self.app.post('/api/clients', data=data, content_type = 'application/json')
        self.assertEqual( resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')
        self.assertIsNotNone( data['id'])

        client_id = data['id']

        resp = self.app.get(u'/api/clients/'+client_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['contact']['email'], 'client3@client3.com')


    def test_client_get(self):
        self.create_admin()
        self.create_client()

        client_id = unicode(self.client.pk)

        sleep(1)
        resp = self.app.get(u'/api/clients/'+client_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['contact']['email'], self.client.contact.email)
        self.assertEqual( data['sectors'], [ sector[0] for sector in ANELLA_SECTORS] )

    def test_client_delete(self):
        self.create_admin()
        self.create_client()

        client_id = unicode(self.client.pk)

        sleep(1)
        resp = self.app.delete('/api/clients/'+client_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get(u'/api/clients/'+client_id)
        self.assertEqual( resp.status_code, 404)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'fail')


    def test_client_put(self):
        self.create_admin()
        self.create_client()

        client_id = unicode(self.client.pk)

        sleep(1)
        data = '''{ "name" : "client3", "sectors" : [ "industry" ], "contact": { "email": "client3@client3.com" } }''' 
        resp = self.app.put('/api/clients/'+client_id, data=data, 
                            content_type='application/json')

        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get(u'/api/clients/'+client_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['contact']['email'], 'client3@client3.com')
        self.assertEqual( data['sectors'], [ "industry" ] )

if __name__ == '__main__':
    unittest.main()

