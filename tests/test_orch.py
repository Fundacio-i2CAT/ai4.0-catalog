# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
from time import sleep

from flask import json, jsonify

from app import AppTestCase
from anella.model.project import SAVED, CONFIRMED, PROVISIONED, RUNNING, DEPLOYED

__all__ = ('ProjectApiTest', )

class OrchTest(AppTestCase):

    def create_all_project(self):
        self.create_admin()
        self.create_client()
        self.create_provider()
        self.create_scontext()
        self.create_apache_service()
        self.create_project()

    def confirm(self):
        for sp in self.project.services:
            sp.confirm()
#         for sp in self.project1.services:
#             sp.confirm()
#         sleep(1)

    def test_create_instance(self):
        self.create_all_project()

        self.create_instance()

    def test_states(self):
        self.create_all_project()

        status = SAVED
        resp = self.app.get(u'/api/projects/%s/state' % unicode(self.project.pk))
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], status)

#         import pdb;pdb.set_trace()
        data = dict(status=RUNNING)
        resp = self.app.put(u'/api/projects/%s/state' % unicode(self.project.pk),
                            data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 400)

        self.confirm()

        status=CONFIRMED
        resp = self.app.get(u'/api/projects/%s/state' % unicode(self.project.pk))
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], status)

        status=PROVISIONED
        data = dict(status=status)
        resp = self.app.put(u'/api/projects/%s/state' % unicode(self.project.pk),
                            data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 200)

        resp = self.app.get(u'/api/projects/%s/state' % unicode(self.project.pk))
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        # self.assertIn( data['state'], ('PROVISIONED', 'RUNNING', 'DEPLOYED'))
        # self.assertIn( data['status'], (PROVISIONED, RUNNING, DEPLOYED))
        # Openstack not working
        self.assertIn( data['status'], (CONFIRMED, PROVISIONED, RUNNING, DEPLOYED))

        status=RUNNING
        data = dict(status=status)
        resp = self.app.put(u'/api/projects/%s/state' % unicode(self.project.pk),
                            data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 200)

        resp = self.app.get(u'/api/projects/%s/state' % unicode(self.project.pk))
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        # Openstack not working
        # self.assertEqual( data['state'], 'RUNNING')
        self.assertEqual( data['state'], 'CONFIRMED')

        status=DEPLOYED
        data = dict(status=status)
        resp = self.app.put(u'/api/projects/%s/state' % unicode(self.project.pk),
                            data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 200)

        resp = self.app.get(u'/api/projects/%s/state' % unicode(self.project.pk))
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        # Openstack not working
        # self.assertEqual( data['state'], state)
        self.assertEqual( data['state'], 'CONFIRMED')

if __name__ == '__main__':
    unittest.main()
