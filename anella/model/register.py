from anella.api.utils import respond_json, read_json_file, create_message_error
from anella.common import get_cfg, put_headers_keystone
from anella.api.service_manager_mailer import ServiceManagerMailer
from anella.api.utils import post, delete, get_keystone_token
from anella.model.user import Client, Provider
from anella.api.keystone import Keystone
import json
from requests import Session


def create_identification(identification):
    key = "CIF"
    if identification['isnif']:
        key = "NIF"
    item = {"key": key,
            "value": identification['value']}
    return item


class Register(object):
    def __init__(self):
        self.path = get_cfg('keystone__url')
        self.user = None
        self.keystone = Keystone()
        self.response_msg = create_message_error(409, 'USER_DUPLICATED')
        self.smm = ServiceManagerMailer()
        self.session = Session()

    def save_keystone(self, data):
        #primero comprobamos que el usuario ha de ser o proveedor o cliente
        if not data['client_role'] and not data['provider_role']:
            return respond_json(create_message_error(400, 'PROVIDER_CLIENT'), 400)
        # login
        response = self.keystone.get_login()
        if response.status_code == 201:
            token = get_keystone_token(response)
            entity = self.keystone.get_project(get_cfg('keystone__project_name'))
            entity_id = entity['keystone_project_id']
            json_data = read_json_file(get_cfg('keystone__data_create_user'))
            json_data['user']['default_project_id'] = entity_id
            json_data['user']['name'] = data['email']
            json_data['user']['password'] = data['password']
            url = self.path + get_cfg('keystone__create_user')
            response = post(self.session, url,
                            put_headers_keystone(token),
                            json_data)
            if response.status_code == 201:
                user_id = json.loads(response.text)['user']['id']
                # grabamos la info en mongo
                if data['provider_role']:
                    self.user = Provider()
                else:
                    self.user = Client()
                try:
                    self.dict_to_mongo_user(data, user_id,
                                            entity_id, str(entity['_id']))
                    self.response_msg = dict(status_code=201)
                except Exception as e:
                    '''
                    Cualquier error que se produzca al intentar grabar en BBDD. 
                    Hemos de borrar el usuario de Keystone
                    '''
                    print e
                    url = url + "/" + user_id
                    delete(self.session, url,
                           put_headers_keystone(token))
                    self.response_msg = create_message_error(400)
                if self.response_msg['status_code'] == 201:
                    self.smm.notify(self.user.email)
            return respond_json(self.response_msg, self.response_msg['status_code'])

    def dict_to_mongo_user(self, data, id_keystone, keystone_project_id, project_id):
        self.user.user_name = data['email']
        self.user.name = data['name']
        self.user.surname = data['surname']
        self.user.email = data['email']
        self.user.company = data['company']
        self.user.address = data['comp_address']
        self.user.phone = data['comp_phone']
        self.user.position = data['comp_position']
        self.user.legal = data['legal']
        self.user.identification = create_identification(data['identification_number'])
        self.user.entity = {'keystone_project_id': keystone_project_id,
                            'entity_id': project_id}
        self.user.keystone_user_id = id_keystone
        self.user.save()
