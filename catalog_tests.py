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

BASE_URL = 'http://dev.anella.i2cat.net:9999'

CLIENT = {'user_name': 'client@i2cat.net', 'password': 'i2cat', 'role': 'User.Client'}
PROVIDER = {'user_name': 'user@i2cat.net', 'password': 'i2cat', 'role': 'User.Provider'}

class CatalogTestCase(unittest.TestCase):
    """Full test"""

    def setUp(self):
        """Initial setup"""
        self._project_ids = []
        self._client = {}
        self._provider = {}

    def login(self, user_name, password, role, expected=200):
        resp = requests.post('{0}/api/session'.format(BASE_URL),
                             headers={'Content-Type': 'application/json'},
                             json={'user_name': user_name, 'password': password})
        assert resp.status_code == expected
        if expected == 200:
            resp_data = json.loads(resp.text)
            assert resp_data['role'] == role
            assert 'id' in resp_data
            print 'Login as {0} with role {1} OK'.format(user_name, role)
            return {'id': resp_data['id'], 'token': resp_data['token']}
        else:
            print 'Expected status code {0} for wrong login OK'.format(resp.status_code)

    def test_01(self):
        """Login Tests"""
        self.login(CLIENT['user_name'], CLIENT['password'], CLIENT['role'])
        self.login(PROVIDER['user_name'], PROVIDER['password'], PROVIDER['role'])
        self.login('user@i2cat.net', 'i2catasd', 'User.Provider', 401)

    def test_02(self, provider_id=None):
        """Services API endpoint"""
        resp = requests.get('{0}/api/services'.format(BASE_URL),
                             headers={'Content-Type': 'application/json'})
        assert resp.status_code == 200
        services = json.loads(resp.text)
        assert 'result' in services
        res = []
        if not provider_id:
            res = services['result']
        else:
            print 'Choosing services for provider {0}'.format(provider_id)
            for serv in services['result']:
                if serv['provider']['_id'] == provider_id:
                    res.append(serv)
        return res

    def test_03(self):
        """Client projects endpoint"""
        print '\nChecking client projects endpoint'
        client = self.login(CLIENT['user_name'], CLIENT['password'], CLIENT['role'])
        headers = {'Authorization': client['token']}
        resp = requests.get('{0}/api/clients/{1}/projects'.format(BASE_URL,
                                                                  client['id']),
                            headers=headers)
        assert resp.status_code == 200
        client_projects = json.loads(resp.text)
        assert 'result' in client_projects
        for proj in client_projects['result']:
            assert proj['client'] == client['id']
        return client_projects['result']

    def create_project(self, provider_id=None, preserve=False):
        """Create project test"""
        tpc = {}
        services = self.test_02(provider_id)
        service = random.choice(services)
        sid = service['_id']
        tpc['services'] = []
        tpc['services'].append({'service': sid})
        tpc['client'] = self._client['id']
        tpc['name'] = str(uuid.uuid4())
        tpc['summary'] = str(uuid.uuid4())
        tpc['description'] = str(uuid.uuid4())
        resp = requests.post('{0}/api/projects'.format(BASE_URL),
                             headers={'Content-Type': 'application/json',
                                      'Authorization': self._client['token']},
                             json=tpc)
        assert resp.status_code in (200, 201)
        project = json.loads(resp.text)
        assert 'id' in project
        if preserve == False:
            self._project_ids.append(project['id'])
        return sid, project['id']

    def test_04(self):
        """Create many projects"""
        print
        nprojects = 100
        print 'Creating {0} projects'.format(nprojects)
        self._client = self.login('client@i2cat.net', 'i2cat', 'User.Client')
        for i in range(0,nprojects):
            self.create_project()
        print 'All projects {0} successfully created OK'.format(nprojects)

    def get_consumer_params(self, service_id):
        """Get consumer params"""
        cpresp = requests.get('{0}/api/services/consumer/params/{1}'.format(BASE_URL,
                                                                            service_id),
                              headers={'Authorization': self._client['token']})
        assert cpresp.status_code == 200
        cpdata = json.loads(cpresp.text)
        assert 'data' in cpdata
        return cpdata['data']

    def stop_project(self, project_id):
        confirm = requests.put('{0}/api/project/{1}/state'.format(BASE_URL,
                                                                  project_id),
                               headers={'Content-Type': 'application/json',
                                        'Authorization': self._client['token']},
                               json={'status': 6})
        max_retries = 10
        deployed_ok = False
        while True:
            state = requests.get('{0}/api/projects/{1}/state'.format(BASE_URL,
                                                                    project_id),
                                headers={'Content-Type': 'application/json',
                                         'Authorization': self._client['token']})
            status = json.loads(state.text)
            print status['project_id'], status['status'], '\t', status['state']
            time.sleep(3)
            max_retries = max_retries-1
            if status['state'] == 'DEPLOYED':
                print 'DEPLOYED state reached OK'
                deployed_ok = True
                break
            if max_retries < 0:
                print 'Timeout waiting project stop'
                break

        if deployed_ok:
            conflict = requests.put('{0}/api/project/{1}/state'.format(BASE_URL,
                                                                       project_id),
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': self._client['token']},
                                    json={'status': 6})
            print 'Trying to stop a stopped service results in {0} OK'.format(conflict.status_code)
            assert not conflict.status_code in (200,201)


    def test_05(self):
        """Approve and instantiate project"""
        print
        self._client = self.login('client@i2cat.net', 'i2cat', 'User.Client')
        self._provider = self.login('user@i2cat.net', 'i2cat', 'User.Provider')
        service_id, project_id = self.create_project(self._provider['id'])
        print service_id
        pending = requests.get('{0}/api/providers/{1}/projects'.format(BASE_URL,
                                                                       self._provider['id']),
                               headers={'Authorization': self._provider['token']})
        assert pending.status_code == 200
        pending_data = json.loads(pending.text)
        assert 'result' in pending_data
        for pproj in pending_data['result']:
            if project_id == pproj['project']['_id']:
                confirm = requests.put('{0}/api/project/{1}/state'.format(BASE_URL,
                                                                      pproj['project']['_id']),
                                       headers={'Content-Type': 'application/json',
                                                'Authorization': self._provider['token']},
                                       json={'status': 3})
                assert confirm.status_code == 200
        print 'Obtaining consumer params for service {0}'.format(service_id)
        cprequired = self.get_consumer_params(service_id)
        print 'Filling consumer params with random values'
        for cpr in cprequired:
            for field in cpr['fields']:
                if field['type'] == 'String':
                    field['value'] = str(uuid.uuid4())
                else:
                    field['value'] = random.randint(0, 10000)
                print field['name'],' = ', field['value']
        print 'Instantiating project'
        instresp = requests.put('{0}/api/projects/{1}/state'.format(BASE_URL,
                                                                    project_id),
                                headers={'Content-Type': 'application/json',
                                         'Authorization': self._client['token']},
                                json={'status': 5, 'consumer_params': cprequired})
        assert instresp.status_code == 200
        max_retries = 10
        instantiation_ok = False
        while True:
            state = requests.get('{0}/api/projects/{1}/state'.format(BASE_URL,
                                                                    project_id),
                                headers={'Content-Type': 'application/json',
                                         'Authorization': self._client['token']})
            try:
                status = json.loads(state.text)
                print status['project_id'], status['status'], '\t', status['state']
            except:
                print 'Error instantiating ...'
                print state.status_code, status['code']
                break
            max_retries = max_retries-1
            if status['state'] == 'RUNNING':
                print 'Instantiation went well'
                instantiation_ok = True
                break
            if max_retries < 0:
                print 'Timeout waiting instantiation'
                break
            if state.status_code != 200:
                print 'Error instantiating ...'
                print state.status_code, status['code']
            time.sleep(20)
        if instantiation_ok:
            print 'Checking stop project feature'
            self.stop_project(project_id)

    def tearDown(self):
        """tearDown"""
        for pro in self._project_ids:
            resp = requests.delete('{0}/api/projects/{1}'.format(BASE_URL, pro),
                                   headers={'Authorization': self._client['token']})
            assert resp.status_code == 200
            delete_data = json.loads(resp.text)
            assert 'status' in delete_data
            assert delete_data['status'] == 'ok'

if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    unittest.main()
