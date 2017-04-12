# coding=utf-8
from anella.api.utils import read_json_file, find_one_in_collection
from anella.common import get_cfg
from anella.api.utils import post_kesytone

def get_keystone_info(file):
    return file['user'], file['password']


class Keystone(object):
    def __init__(self):
        self.keystone_admin, self.keystone_admin_pass = \
            get_keystone_info(read_json_file(get_cfg('keystone__file')))
        self.path = get_cfg('keystone__url')

    def get_project(self, name_project):
        """
        Consultamos el proyecto/entidad en Mongo, ya que guardamos cierta información de la entitiy
        y la API de keystone no ofrece un findByName.
        :return: 
        """
        return find_one_in_collection('entities', {"name": name_project})

    def get_login(self, session):
        json_data = read_json_file(get_cfg('keystone__data_login'))
        json_data['auth']['identity']['password']['user']['name'] = self.keystone_admin
        json_data['auth']['identity']['password']['user']['password'] = self.keystone_admin_pass
        url = self.path + get_cfg('keystone__login')
        return post_kesytone(session, url, None, json_data)
