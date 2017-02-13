#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Anella 4.0 Service Manager Tests"""

import json
import unittest
import requests
import random
import time
import uuid

BASE_URL = 'http://dev.anella.i2cat.net:9999'

TEST_PROJECT_CONTEXT = {
    "name": "Test de creació de projecte",
    "summary":"Test de creació de projecte",
    "description":"Test de creació de projecte"
}

class CatalogTestCase(unittest.TestCase):
    """Full test"""

    def setUp(self):
        """Initial setup"""
        self._project_ids = []

    def login(self, user_name, password, role, expected=200):
        resp = requests.post('{0}/api/session'.format(BASE_URL),
                             headers={'Content-Type': 'application/json'},
                             json={'user_name': user_name, 'password': password})
        assert resp.status_code == expected
        if expected == 200:
            resp_data = json.loads(resp.text)
            assert resp_data['role'] == role
            assert 'id' in resp_data
            return resp_data['id']


    def test_01(self):
        """Login Tests"""
        self.login('client@i2cat.net', 'i2cat', 'User.Client')
        self.login('user@i2cat.net', 'i2cat', 'User.Provider')
        self.login('user@i2cat.net', 'i2catasd', 'User.Provider', 401)

    def test_04(self):
        """Services API endpoint"""
        resp = requests.get('{0}/api/services'.format(BASE_URL),
                             headers={'Content-Type': 'application/json'})
        assert resp.status_code == 200
        services = json.loads(resp.text)
        assert 'result' in services
        return services['result']

    def test_05(self):
        """Client projects endpoint"""
        client_id = self.login('client@i2cat.net', 'i2cat', 'User.Client')
        resp = requests.get('{0}/api/clients/{1}/projects'.format(BASE_URL,
                                                                  client_id))
        assert resp.status_code == 200
        client_projects = json.loads(resp.text)
        assert 'result' in client_projects
        return client_projects['result']

    def create_project(self, preserve=False):
        """Create project test"""
        tpc = TEST_PROJECT_CONTEXT
        client_id = self.login('client@i2cat.net', 'i2cat', 'User.Client')
        services = self.test_04()
        service = random.choice(services)
        sid = service['_id']
        tpc['services'] = []
        tpc['services'].append({'service': sid})
        tpc['client'] = client_id
        tpc['name'] = str(uuid.uuid4())
        resp = requests.post('{0}/api/projects'.format(BASE_URL),
                             headers={'Content-Type': 'application/json'},
                             json=tpc)
        assert resp.status_code in (200, 201)
        project = json.loads(resp.text)
        assert 'id' in project
        if preserve == False:
            self._project_ids.append(project['id'])
        return sid, project['id']

    def test_06(self):
        """Create many projects"""
        self.create_project()
        self.create_project()
        self.create_project()
        self.create_project()
        self.create_project()
        self.create_project()
        self.create_project()

    def get_consumer_params(self, service_id):
        """Get consumer params"""
        cpresp = requests.get('{0}/api/services/consumer/params/{1}'.format(BASE_URL,
                                                                            service_id))
        assert cpresp.status_code == 200
        cpdata = json.loads(cpresp.text)
        assert 'data' in cpdata
        return cpdata['data']

    def test_07(self):
        """Approve and instantiate project"""
        user_id = self.login('user@i2cat.net', 'i2cat', 'User.Provider')
        service_id, project_id = self.create_project(False)
        pending = requests.get('{0}/api/providers/{1}/projects'.format(BASE_URL,
                                                                       user_id))
        assert pending.status_code == 200
        pending_data = json.loads(pending.text)
        assert 'result' in pending_data
        for pproj in pending_data['result']:
            if project_id == pproj['project']['_id']:
                confirm = requests.put('{0}/api/sprojects/{1}'.format(BASE_URL,
                                                                      pproj['_id']),
                                       headers={'Content-Type': 'application/json'},
                                       json={'status': 3})
                assert confirm.status_code == 200
        cprequired = self.get_consumer_params(service_id)
        for cpr in cprequired:
            for field in cpr['fields']:
                if field['type'] == 'String':
                    field['value'] = str(uuid.uuid4())
                else:
                    field['value'] = random.randint(0, 10000)
        instresp = requests.put('{0}/api/projects/{1}/state'.format(BASE_URL,
                                                                   project_id),
                               headers={'Content-Type': 'application/json'},
                               json={'status': 5, 'consumer_params': cprequired})
        assert instresp.status_code == 200
        url = '{0}/api/projects/{1}'.format(BASE_URL, project_id)
        while True:
            time.sleep(10)
            resp = requests.get(url)
            assert resp.status_code == 200
            nsi = json.loads(resp.text)
            if nsi['status'] != 9:
                print nsi
                break

    def tearDown(self):
        """tearDown"""
        for pro in self._project_ids:
            resp = requests.delete('{0}/api/projects/{1}'.format(BASE_URL, pro))
            assert resp.status_code == 200
            delete_data = json.loads(resp.text)
            assert 'status' in delete_data
            assert delete_data['status'] == 'ok'

if __name__ == '__main__':
    unittest.main()
