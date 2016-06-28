# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
from time import sleep

from flask import json, jsonify

from app import AppTestCase

__all__ = ('ProjectApiTest', )

class ProjectApiTest(AppTestCase):

    def test_empty_get(self):
        resp = self.app.get('/api/projects')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 0)
        self.assertEqual( data['status'], 'ok')

    def create_all_project(self):
        self.create_admin()
        self.create_client()
        self.create_provider()
        self.create_scontext()
        self.create_apache_service()
        self.create_project()
        sleep(1)

    def test_projects_get(self):
        self.create_all_project()

        resp = self.app.get(u'/api/projects')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 1)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get('/api/projects?name=project1')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertEqual( data['count'], 1)

    def _test_projects_post(self):
        self.create_admin()
        self.create_client()
        self.create_provider()
        sleep(1)

        data = { "name" : "project3", 
                 "client" : unicode(self.client.pk),
               }
        resp = self.app.post('/api/projects', data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')
        self.assertIsNotNone( data['id'])

        project_id = data['id']

        resp = self.app.get(u'/api/projects/'+project_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)


    def test_project_get(self):
        self.create_all_project()

        project_id = unicode(self.project.pk)

        sleep(1)
        resp = self.app.get(u'/api/projects/'+project_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

    def _test_project_delete(self):
        self.create_all_project()

        project_id = unicode(self.project.pk)

        sleep(1)
        resp = self.app.delete('/api/projects/'+project_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get(u'/api/projects/'+project_id)
        self.assertEqual( resp.status_code, 404)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'fail')


    def _test_project_put(self):
        self.create_all_project()

        project_id = unicode(self.project.pk)

        sleep(1)
        data = { "name" : "project3", 
                 "client" : unicode(self.client.pk),
                 "status" : 1,
               }
        resp = self.app.put('/api/projects/'+project_id, data=json.dumps(data), 
                            content_type='application/json')

        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

        resp = self.app.get(u'/api/projects/'+project_id)
        self.assertEqual( resp.status_code, 200)

    def _test_sproject_post(self):
        self.create_all_project()

        project_id = unicode(self.project.pk)
        service_id = unicode(self.cloud.pk)

        data = { 
                 "service" : unicode(self.cloud.pk),
                 "context" : {
                    "param1" : "val1",
                    "param2" : "val2",
                 }
               }
        resp = self.app.post('/api/projects/'+project_id+'/services', data=json.dumps(data), content_type = 'application/json')
        self.assertEqual( resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')
        self.assertIsNotNone( data['id'])

        sproject_id = data['id']

    def _test_sprojects_get(self):
        self.create_all_project()

        sproject_id = unicode(self.sproject.pk)

        sleep(1)
        resp = self.app.get(u'/api/sprojects/'+sproject_id)
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

        resp = self.app.get(u'/api/sprojects')
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['count'], 1)

    def test_client_projects_get(self):
        self.create_all_project()

        resp = self.app.get(u'/api/clients/%s/projects' % unicode(self.client.pk))
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

#         self.assertEqual( data['count'], 1)
        self.assertEqual( data['status'], 'ok')

#         resp = self.app.get('/api/projects?name=project1')
#         self.assertEqual( resp.status_code, 200)
#         data = json.loads(resp.data)
# 
#         self.assertEqual( data['count'], 1)

    def test_provider_projects_get(self):
        self.create_all_project()

        resp = self.app.get(u'/api/providers/%s/projects' % unicode(self.provider.pk))
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)

#         self.assertEqual( data['count'], 1)
        self.assertEqual( data['status'], 'ok')

    def _test_project_provision(self):
        self.create_all_project()

        resp = self.app.get(u'/api/projects/%s/provision' % unicode(self.project.pk))
        self.assertEqual( resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual( data['status'], 'ok')

if __name__ == '__main__':
    unittest.main()
