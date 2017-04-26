# coding=utf-8
from anella.api.utils import read_json_file, find_one_in_collection, get_keystone_token, create_keystone_headers
from anella.common import get_cfg
from anella.api.utils import post
from requests import Session
import json


def get_keystone_info(file):
    return file['user'], file['password']


class Keystone(object):
    def __init__(self):
        self.keystone_admin, self.keystone_admin_pass = \
            get_keystone_info(read_json_file(get_cfg('keystone__file')))
        self.path = get_cfg('keystone__url')
        self.session = Session()

    def get_project(self, name_project, data):
        """
        Consultamos el proyecto/entidad en Mongo, ya que guardamos cierta información de la entitiy
        y la API de keystone no ofrece un findByName.
        :return: 
        """
        entity = find_one_in_collection('entities', {"name": name_project})
        entity_id = entity['keystone_project_id']
        json_data = read_json_file(get_cfg('keystone__data_create_user'))
        json_data['user']['default_project_id'] = entity_id
        json_data['user']['name'] = data['email']
        json_data['user']['password'] = data['password']
        return json_data, entity_id, entity

    def get_login(self):
        json_data = read_json_file(get_cfg('keystone__data_login'))
        json_data['auth']['identity']['password']['user']['name'] = self.keystone_admin
        json_data['auth']['identity']['password']['user']['password'] = self.keystone_admin_pass
        url = self.path + get_cfg('keystone__login')
        return post(self.session, url, None, json_data)

    def get_users(self):
        response = self.get_login()
        url = self.path + get_cfg('keystone__create_user')
        return self.session.get(url, headers=create_keystone_headers(get_keystone_token(response)))

    def patch_user(self, user_id, info):
        response = self.get_login()
        url = self.path + get_cfg('keystone__create_user') + "/" + user_id
        return self.session.patch(url, data=json.dumps(self.get_json_data(info)),
                                  headers=create_keystone_headers(get_keystone_token(response)))

    def get_json_data(self, info):
        if isinstance(info, bool):
            json_data = read_json_file(get_cfg('keystone__data_patch_user'))
            json_data['user']['enabled'] = info
        else:
            json_data = read_json_file(get_cfg('keystone__data_patch_password_user'))
            json_data['user']['password'] = info
        return json_data

    def change_password(self, user_id, password):
        response = self.get_login()
        url = self.path + get_cfg('keystone__create_user') + "/" + user_id + '/password'
        json_data = read_json_file(get_cfg('keystone__data_change_password_user'))
        json_data['user']['password'] = password['password']
        json_data['user']['original_password'] = password['original_password']
        return self.session.post(url, data=json.dumps(json_data),
                                 headers=create_keystone_headers(get_keystone_token(response)))
