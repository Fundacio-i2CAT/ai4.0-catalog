# -*- coding: utf-8 -*-

import os

from anella.common import *
from anella.api.utils import respond_json
from anella.model.service import get_service_cls, get_service_types
from anella.model.service import AppService, VMImage
from anella import configuration as _cfg
from anella.model.service import create_service
from flask import request
from werkzeug.utils import secure_filename
import glob
import hashlib
from anella.orch import Orchestrator

from anella.api.utils import ColRes, ItemRes, Resource, item_to_json, ObjectId

class ServicesRes(ColRes):
    collection= 'services'
    _cls = AppService
    name= 'Services'
    fields = '_id,name,summary,service_type,provider,sectors,created_at,updated_at,price_initial,price_x_hour'.split(',')
    filter_fields = 'name,keywords,sectors,activated'.split(',')

    def post(self):
        item = get_json()
        return create_service(item)

    def _item_from_json(self, data):
        service_cls = get_service_cls( data.get('service_type') )
        if service_cls:
            self._cls = service_cls
        item = ColRes.item_from_json(self, data)
        item['_cls'] = service_cls._class_name
        # obj = service_cls.from_json(item)
        return item

    def _item_to_json(self, item):
        sitem = ColRes._item_to_json(self, item)
        provider_id = sitem['provider']
        if provider_id:
            provider = get_db(_cfg.database__database_name)['users'].find_one({'_id':ObjectId(provider_id)})
            sitem['provider'] = item_to_json(provider, ['_id', 'user_name'])
        return sitem

    def _get_items(self, skip=0, limit=1000, **values):
        return super(ServicesRes, self)._get_items(skip, limit, dict(activated=True))

class ServiceRes(ItemRes):
    collection= 'services'
    _cls = AppService
    name= 'Service'
    fields = '_id,name,summary,description,service_type,provider,sectors,keywords,link,' \
             'created_at,created_by,updated_at,updated_by,price_initial,price_x_hour'.split(',')

    def _item_to_json(self, item):
        sitem = ItemRes._item_to_json(self, item)
        provider_id = sitem['provider']
        if provider_id:
            provider = get_db(_cfg.database__database_name)['users'].find_one({'_id':ObjectId(provider_id)})
            sitem['provider'] = item_to_json(provider, ['_id', 'user_name'])
        return sitem


class ServiceTypesRes(Resource):

    def get(self):
        return [ dict(name=st[0], description=st[1][1]) for st in get_service_types()]


class VMImageRes(Resource):
    def post(self):
        try:
            _file = request.files['file']
            vm_image = VMImage(_file.filename, _file)
            extension_file = os.path.splitext(_file.filename)[1]
            data = vm_image.save_image()
            response = dict(vm_image=unicode(data), name_image=_file.filename,
                            vm_image_format=extension_file[1:])
            return respond_json(response, status=200)
        except Exception as e:
            response = dict(status='nok', msg="Error %s %s" % (e, e.message))
            return respond_json(response, status=400)


class ServiceConsumerParamsRes(ColRes):
    def get(self, id):
        service = get_db(_cfg.database__database_name)['services'].find_one({'_id': ObjectId(id)})
        if service is None:
            response = dict(status="nok", msg="Service not found: %s" % id)
            return respond_json(response, status=404)

        data = {}
        if 'consumer_params' in service['context']:
            data = service['context']['consumer_params']
        response = dict(data=data)
        return respond_json(response, status=200)


class VMImageResourceRes(Resource):
    def post(self):
        _file = request.files['file']
        filename = secure_filename(_file.filename)
        _file.save(os.path.join(_cfg.repository__download, filename))


class VMImageUnchunkedRes(Resource):
    def post(self):
        data = get_json()
        filename = '{0}{1}'.format(_cfg.repository__download, data['filename'])
        path_repository = '{0}{1}{2}'.format(_cfg.repository__download, data['uuid'], "*")
        try:
            outfile = open(filename, "w")
            for line in sorted(glob.glob(path_repository)):
                f = open(line)
                f_read = f.read()
                f.close()
                outfile.write(f_read)
                os.remove(line)
            outfile.close()
            md5sum = self.checksum_md5(filename)
            if data['md5sum'] == md5sum:
                response = dict(md5="ok", name_image=data['filename'])
                return respond_json(response, status=200)
            else:
                #Devolvemos 409
                response = dict(status="nok", msg="Error to upload file. MD5 not equal: %s" %data['filename'])
                return respond_json(response, status=409)
        except Exception as e:
            self.delete_files_tmp(path_repository, filename)
            response = dict(status="nok", msg="Error to upload file: %s" %e)
            return respond_json(response, status=500)

    def checksum_md5(self, filename):
        md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def delete_files_tmp(self, path_repository, filename):
        for line in sorted(glob.glob(path_repository)):
            os.remove(line)
        if os.path.exists(filename):
            os.remove(filename)


class VMImageUploadBDRes(Resource):
    def post(self):
        data = get_json()
        try:
            vm_image = VMImage(data['filename'])
            data_vm = vm_image.save_image_2()
            os.remove(_cfg.repository__download + data['filename'])
            response = dict(vm_image=unicode(data_vm), name_image=data['filename'])
            return respond_json(response, status=200)
        except Exception as e:
            os.remove(_cfg.repository__download + data['filename'])
            response = dict(status="nok", msg="Error to upload file: %s" % e)
            return respond_json(response, status=500)


class Flavors(ItemRes):
    def get(self, id):
        orch = Orchestrator(debug=False)
        return orch.get_flavors(id)


class Pop(ItemRes):
    def get(self):
        orch = Orchestrator(debug=False)
        return orch.get_pop()
