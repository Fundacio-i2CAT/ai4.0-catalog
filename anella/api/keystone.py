# coding=utf-8
from anella.api.utils import read_json_file, find_one_in_collection
from anella.common import get_cfg


def get_keystone_info(file):
    return file['user'], file['password']


class Keystone(object):
    def __init__(self):
        self.keystone_admin, self.keystone_admin_pass = \
            get_keystone_info(read_json_file(get_cfg('keystone__file')))

    def get_project(self, name_project):
        """
        Consultamos el proyecto en Mongo, ya que guardamos cierta información de la entitiy
        y la API de keynstone no ofrece un findByName.
        :return: 
        """
        return find_one_in_collection('entities', {"name": name_project})
