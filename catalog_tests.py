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
import hashlib
from urlparse import urlparse
from pymongo import MongoClient
from bson.objectid import ObjectId

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASE_URL = 'http://localhost:9999'

CLIENT = {'user_name': 'client@i2cat.net',
          'password': 'i2cat', 'role': 'User.Client'}
PROVIDER = {'user_name': 'user@i2cat.net',
            'password': 'i2cat', 'role': 'User.Provider'}
ADMIN = {'user_name': 'admin',
         'password': 'i2cat', 'role': 'User.Administrator'}

SAMPLE_CLOUD_IMAGE = '../imgs/trusty-server-cloudimg-amd64-disk1.img'
SAMPLE_ICON = '../Pictures/pass.png'
SAMPLE_SERVICE_DESCRIPTOR = {'name':'',
                             'description':'',
                             'summary':'',
                             'service_type':'iss',
                             'provider':'',
                             'price_initial':1,
                             'price_x_hour':1,
                             'consumer_params':[],
                             'flavor':'VM.S1',
                             'pop_id':21,
                             'name_image':'trusty-server-cloudimg-amd64-disk1.img',
                             'vm_image':'5912bbccbcc49d35e215cb0c',
                             'vm_image_format':'QCOW2',
                             'runtime_params':[{'name':'floating_ip', 'type':'String', 'required':True, 'desc':'floating_ip'}]}

CLIENT_REGISTER_FORM = {
    'name': 'Test',
    'surname': 'Test_sn',
    'email': 'email@example.com',
    'company': 'Test_cmp',
    'comp_address': 'Test_cmp_addr',
    'comp_phone': 'Test_cmp_ph',
    'comp_position': 'Test_pos',
    'client_role': True,
    'provider_role': False,
    'legal': False,
    'password': 'secretsecret',
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

class CatalogTestCase(unittest.TestCase):
    """Full test"""

    def setUp(self):
        """Initial setup"""
        self._project_ids = []
        self._client = {}
        self._provider = {}

    def register(self):
        """Register function"""
        print
        CLIENT_REGISTER_FORM['email'] = str(uuid.uuid4())+'@example.com'
        CLIENT_REGISTER_FORM['identification_number']['value'] = nif_generator()
        resp = requests.post('{0}/api/register'.format(BASE_URL),
                             headers={'Content-Type': 'application/json'},
                             json=CLIENT_REGISTER_FORM)
        print resp.status_code
        assert resp.status_code == 204
        # with open('keys/oauth_eurecat.json') as fhandle:
        #     authorization = json.load(fhandle)
        # url = 'https://84.88.76.5:8244/1.0/LmpApiI2cat/people/{0}'.format(data['id'])
        # delete_resp = requests.delete(url, verify=False,
        #                               headers=authorization['headers'])
        # assert delete_resp.status_code == 204
        # print 'Successfully removed test user'
        return

    def login(self, user_name, password, role, expected=200):
        """Login function, in case of success returns the token and user id"""
        resp = requests.post('{0}/api/session'.format(BASE_URL),
                             headers={'Content-Type': 'application/json'},
                             json={'user_name': user_name,
                                   'password': password})
        assert resp.status_code == expected
        if expected == 200:
            resp_data = json.loads(resp.text)
            assert resp_data['role'] == role
            assert 'id' in resp_data
            print 'Login as {0} with role {1} OK'.format(user_name, role)
            return {'id': resp_data['id'], 'token': resp_data['token']}
        else:
            print 'Expected status {0} wrong login OK'.format(resp.status_code)

    def test_01(self):
        """Login Tests"""
        self.login(CLIENT['user_name'],
                   CLIENT['password'],
                   CLIENT['role'])
        self.login(PROVIDER['user_name'],
                   PROVIDER['password'],
                   PROVIDER['role'])
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
        client = self.login(CLIENT['user_name'],
                            CLIENT['password'],
                            CLIENT['role'])
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
        for i in range(0, nprojects):
            print i,
            self.create_project()
        print
        print 'All projects {0} successfully created OK'.format(nprojects)

    def get_consumer_params(self, service_id):
        """Get consumer params"""
        url = '{0}/api/services/consumer/params/{1}'.format(BASE_URL, service_id)
        cpresp = requests.get(url, headers={'Authorization': self._client['token']})
        assert cpresp.status_code == 200
        cpdata = json.loads(cpresp.text)
        assert 'data' in cpdata
        return cpdata['data']

    def stop_project(self, project_id):
        """Stops a project"""
        requests.put('{0}/api/project/{1}/state'.format(BASE_URL,
                                                        project_id),
                     headers={'Content-Type': 'application/json',
                              'Authorization': self._client['token']},
                     json={'status': 6})
        max_retries = 10
        deployed_ok = False
        while True:
            url = '{0}/api/projects/{1}/state'.format(BASE_URL, project_id)
            state = requests.get(url, headers={'Content-Type': 'application/json',
                                               'Authorization': self._client['token']})
            status = json.loads(state.text)
            print status['project_id'], status['status'], '\t', status['state']
            time.sleep(5)
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
            assert not conflict.status_code in (200, 201)

    def start_project(self, project_id):
        """Starts a project"""
        requests.put('{0}/api/project/{1}/state'.format(BASE_URL,
                                                        project_id),
                     headers={'Content-Type': 'application/json',
                              'Authorization': self._client['token']},
                     json={'status': 5})
        max_retries = 2
        running_ok = False
        while True:
            url = '{0}/api/projects/{1}/state'.format(BASE_URL, project_id)
            state = requests.get(url, headers={'Content-Type': 'application/json',
                                               'Authorization': self._client['token']})
            status = json.loads(state.text)
            print status['project_id'], status['status'], '\t', status['state']
            time.sleep(5)
            max_retries = max_retries-1
            if status['state'] == 'RUNNING':
                print 'RUNNING state reached OK'
                running_ok = True
                break
            if max_retries < 0:
                print 'Timeout waiting project start'
                break

        if running_ok:
            conflict = requests.put('{0}/api/project/{1}/state'.format(BASE_URL,
                                                                       project_id),
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': self._client['token']},
                                    json={'status': 5})
            print 'Trying to start a running service results in {0} OK'.format(conflict.status_code)
            assert not conflict.status_code in (200, 201)

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
                print field['name'], ' = ', field['value']
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
            print 'Checking start project feature'
            self.start_project(project_id)

    def test_06(self):
        """New user register test"""
        print
        print 'Registering new user'
        self.register()

    def pop_data(self):
        """PoP related tests"""
        print
        print 'Testing PoP queries'
        provider = self.login(PROVIDER['user_name'],
                              PROVIDER['password'],
                              PROVIDER['role'])
        headers = {'Authorization': provider['token']}
        popresp = requests.get('{0}/api/services/pop'.format(BASE_URL),
                               headers=headers)
        assert popresp.status_code == 200
        pop_data = json.loads(popresp.text)
        if len(pop_data) > 0:
            flavresp = requests.get('{0}/api/services/flavors/{1}'.format(BASE_URL, pop_data[0]['pop_id']),
                                    headers=headers)
            assert flavresp.status_code == 200
            flav_data = json.loads(flavresp.text)
            flavor = random.choice(flav_data['flavors'])
            return {'pop_id': pop_data[0]['pop_id'],
                    'flavor': flavor['name']}

    def read_in_chunks(self, file_object, chunk_size=10000*1024):
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def test_08(self):
        """Create service test"""
        print
        print 'Testing service creation'
        provider = self.login(PROVIDER['user_name'],
                              PROVIDER['password'],
                              PROVIDER['role'])
        headers = {'Authorization': provider['token']}
        fileid = str(uuid.uuid4())
        with open(SAMPLE_CLOUD_IMAGE, 'rb') as fhandle:
            nchunk = 0
            checksum = hashlib.md5()
            for piece in self.read_in_chunks(fhandle):
                label = str(nchunk).zfill(6)
                print label,
                files = {'file': ('{0}_{1}'.format(fileid, label), piece, 'application/octet-stream')}
                checksum.update(piece)
                resp = requests.post('{0}/api/services/vmimage/chunked'.format(BASE_URL),
                                     headers=headers, files=files)
                assert resp.status_code == 200
                nchunk = nchunk+1
            md5sum = checksum.hexdigest()
            print
            print str(md5sum)
        unchresp = requests.post('{0}/api/services/vmimage/unchunked'.format(BASE_URL),
                                 headers=headers, json={'filename': SAMPLE_CLOUD_IMAGE,
                                                        "uuid": fileid, "md5sum": str(md5sum)})
        assert unchresp.status_code == 200
        data = json.loads(unchresp.text)
        assert 'filename_uuid' in data
        uploresp = requests.post('{0}/api/services/vmimage/upload'.format(BASE_URL),
                                 headers=headers, json={'filename': SAMPLE_CLOUD_IMAGE,
                                                        'filename_uuid': data['filename_uuid']})
        image_data = json.loads(uploresp.text)
        assert uploresp.status_code == 200
        pop_data = self.pop_data()
        ssd = SAMPLE_SERVICE_DESCRIPTOR
        ssd['name'] = str(uuid.uuid4())
        ssd['description'] = str(uuid.uuid4())
        ssd['summary'] = str(uuid.uuid4())
        ssd['provider'] = provider['id']
        ssd['flavor'] = pop_data['flavor']
        ssd['pop_id'] = pop_data['pop_id']
        ssd['name_image'] = str(uuid.uuid4())
        ssd['vm_image'] = image_data['vm_image']
        with open(SAMPLE_ICON, 'rb') as fhandle:
            ssd['service_icon'] = fhandle.read().encode('base64')
        create_service_resp = requests.post('{0}/api/services'.format(BASE_URL),
                                            headers=headers, json=ssd)
        assert create_service_resp.status_code == 201
        service_data = json.loads(create_service_resp.text)
        publish_resp = requests.put('{0}/api/services/{1}'.format(BASE_URL, service_data['id']),
                                    headers=headers, json={'activated': True})
        assert publish_resp.status_code == 200
        unpublish_resp = requests.put('{0}/api/services/{1}'.format(BASE_URL, service_data['id']),
                                      headers=headers, json={'activated': False})
        assert unpublish_resp.status_code == 200
        self.delete_service(service_data['id'])

    def delete_service(self, service_id):
        print
        print 'Deleting service {0}'.format(service_id)
        uparse = urlparse(BASE_URL)
        mclient = MongoClient('mongodb://{0}:27017'.format(uparse.hostname))
        anella = mclient['anella']
        service = anella['services'].find_one({'_id': ObjectId(service_id)})
        anella_repo = mclient['anella_repository']
        image_file = anella_repo['fs.files'].find_one({'_id': ObjectId(service['context']['vm_image'])})
        anella_repo['fs.chunks'].remove({'files_id': ObjectId(image_file['_id'])})
        anella_repo['fs.files'].remove({'_id': ObjectId(image_file['_id'])})
        anella['services'].remove({'_id': ObjectId(service_id)})
        mclient.close()

    def test_09(self):
        """Admin user management tests"""
        print
        admin = self.login(ADMIN['user_name'], ADMIN['password'], ADMIN['role'])
        print admin['id']
        print admin['token']
        headers = {'Authorization': admin['token']}
        users_resp = requests.get('{0}/api/crud/users'.format(BASE_URL),
                                  headers=headers)
        assert users_resp.status_code == 200
        users_data = json.loads(users_resp.text)
        user = random.choice(users_data['result'])
        while user['activated']:
            user = random.choice(users_data['result'])
        user_activation = requests.put('{0}/api/crud/users/{1}'.format(BASE_URL, user['_id']),
                                       headers=headers, json={'activated': True})
        assert user_activation.status_code == 204
        user_desactivation = requests.put('{0}/api/crud/users/{1}'.format(BASE_URL, user['_id']),
                                          headers=headers, json={'activated': False})
        assert user_desactivation.status_code == 204

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
