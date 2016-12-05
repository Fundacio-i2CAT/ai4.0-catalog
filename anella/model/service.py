# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from partner import Partner, Provider, Client, ANELLA_SECTORS
from gridfs import GridFS
from anella import configuration as _cfg
from anella.common import get_db
from bson.objectid import ObjectId
from anella.api.utils import respond_json
import os
import sys
# TODO: Service types should be dynamic and use as options to validate field

_service_types = {}

tenor_url = "http://%s:%s" % (_cfg.tenor__host, _cfg.tenor__port)

def register_service_type(name,cls, des):
    _service_types[name]=(cls,des)

def get_service_type(cls):
    for n,t in _service_types.items():
        if cls==t[0]:
            return n

def get_service_cls(name):
    return _service_types[name]

def get_service_types():
    return _service_types.items()

class ServiceDescription(Document, Base):
    """
    """
    meta = {'allow_inheritance': True, 'collection': 'services',
            'indexes': ['name', ] }

    # Collection fields
    name = StringField(max_length=40, required=True, unique=True)
    summary = StringField(max_length=120)
    description = StringField()
    service_type = StringField(default='app')

    provider = ObjectIdField()
    keywords = ListField(StringField(max_length=40))
    sectors = ListField(StringField(choices=ANELLA_SECTORS))
    link = URLField()
    context = DictField()

    def set_name(self, name):
        self.name = name

    def set_summary(self, summary):
        self.summary = summary

    def set_description(self, description):
        self.description = description

    def set_service_type(self, service_type):
        self.service_type = service_type

    def set_provider(self, provider):
        self.provider = ObjectId(provider)

    def set_context(self, data):
        self.context = create_context(data)

class AppService(ServiceDescription):
    type_name = 'App'  # A type name to use in UI
    scheme = 'service-scheme.json'


class ISService(ServiceDescription):
    type_name = 'Infrastructure'  # A type name to use in UI
    scheme = 'cloud-service-scheme.json'

    service_type = StringField(default='iss')

register_service_type('app', AppService, 'App')
register_service_type('iss', ISService, 'Infraestructura')


class VMImage:
    type_name = 'vm_image'

    url = None
    id = ObjectIdField()
    path_image = None
    name_image = None
    image_file = None

    def __init__(self, name_image):
        self.grid_fs = GridFS(get_db(_cfg.database__database_repository))
        self.name_image = name_image
        #self.image_file = image_file

    def set_id(self, id_image):
        self.id = ObjectId(id_image)

    def set_path_image(self, path_image):
        self.path_image = path_image

    def set_name_image(self, name_image):
        self.name_image = name_image

    def get_image(self):
        print self.id
        grid_fs_file = self.grid_fs.find_one({'_id': ObjectId(self.id)})
        file_path = '{0}{1}'.format(_cfg.repository__path, self.name_image)
        image_file = open(file_path, 'w')
        for chunk in grid_fs_file:
            image_file.write(chunk)
        image_file.close()

    def save_image(self):
        file_id = self.get_file_id()
        grid_fs_file = self.grid_fs.find_one(file_id)
        data = str(grid_fs_file._id)
        grid_fs_file.close()
        return data

    def save_image_2(self):
        image_file = self.grid_fs.new_file()
        image_file.filename = self.name_image
        file_path = '{0}{1}'.format(_cfg.repository__download, self.name_image)
        with open(file_path) as file_:
            file_size = os.path.getsize(file_path)
            for chunk_start, chunk_size in self.get_chunks(file_size):
                file_chunk = file_.read(chunk_size)
                image_file.write(file_chunk)
        image_file.close()
        grid_fs_file = self.grid_fs.find_one(image_file._id)
        data = str(grid_fs_file._id)
        grid_fs_file.close()
        return data

    def get_chunks(self, file_size):
        chunk_start = 0
        chunk_size = 0x20000  # 131072 bytes, default max ssl buffer size
        while chunk_start + chunk_size < file_size:
            yield (chunk_start, chunk_size)
            chunk_start += chunk_size
            print file_size % chunk_start
        final_chunk_size = file_size - chunk_start
        yield (chunk_start, final_chunk_size)

    def delete_image(self):
        self.grid_fs.delete(self.id)


    def get_file_id(self):
        #image_file = open(self.path_image, 'r')
        return self.grid_fs.put(self.image_file, filename=self.name_image)

def create_service(item):
    service = set_service(item)
    if service is not None:
        try:
            service.save()
            response = dict(status='ok', id=unicode(service.pk), msg="Service created.")
            return respond_json(response, status=201)
        except Exception as e:
            print e
            #delete_image_vm(service.context['vm_image'])
    response = dict(status='nok', msg="Error create service")
    return respond_json(response, status=400)


def set_service(data):
    service = ServiceDescription()
    try:
        service.set_name(data.pop('name'))
        service.set_summary(data.pop('summary'))
        service.set_description(data.pop('description'))
        service.set_service_type(data.pop('service_type'))
        service.set_provider(data.pop('provider'))
        service.set_context(data)
    except Exception as e:
        print e
        '''
        if item is not None:
             delete_image_vm(item.get('vm_image'))
        '''
        service = None
    return service

'''
def delete_image_vm(vm_image_id):
    vm_image = VMImage()
    vm_image.id = vm_image_id
    vm_image.delete_image()


def set_vm_image(data):
    vm_image = VMImage()
    vm_image.set_name_image(data.get('name_image'))
    vm_image.set_path_image(data.pop('url_image'))
    vm_image.set_id(vm_image.save_image())
    data['vm_image'] = vm_image.id
    return data
'''

def create_context(data):
    context = dict(vm_image=data.get("vm_image"), flavor=data.pop("flavor"),
                   consumer_params=data.pop("consumer_params"), runtime_params=data.pop("runtime_params"),
                   tenor_url=tenor_url, name_image=data.pop("name_image"),
                   vm_image_format=data.pop("vm_image_format"))

    return context