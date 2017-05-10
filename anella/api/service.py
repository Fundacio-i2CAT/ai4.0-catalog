# -*- coding: utf-8 -*-

import os

from anella.common import *
from anella.api.utils import respond_json, count_collection, get_int
from anella.model.service import get_service_cls, get_service_types
from anella.model.service import AppService, VMImage
from anella import configuration as _cfg
from anella.model.service import create_service
from anella.model.service_icon import ServiceIcon
from flask import request
from werkzeug.utils import secure_filename
import glob
import hashlib
from anella.orch import Orchestrator
from datetime import datetime
from anella.api.utils import ColRes, ItemRes, Resource, item_to_json, ObjectId
import uuid
from anella.security.authorize import get_exists_user, get_authorize, post_authorize

class ServicesRes(ColRes):
    collection = 'services'
    _cls = AppService
    name = 'Services'
    fields = '_id,name,summary,service_type,provider,sectors,created_at,updated_at,price_initial,price_x_hour,service_icon'.split(',')
    filter_fields = 'name,keywords,sectors,activated'.split(',')

    @get_exists_user('User.Provider')
    @post_authorize('User.Provider', 'provider')
    def post(self):
        item = get_json()
        return create_service(item)

    def _item_from_json(self, data):
        service_cls = get_service_cls(data.get('service_type'))
        if service_cls:
            self._cls = service_cls
        item = ColRes.item_from_json(self, data)
        item['_cls'] = service_cls._class_name
        # obj = service_cls.from_json(item)
        return item

    def _item_to_json(self, item):
        sitem = ColRes._item_to_json(self, item)
        if 'service_icon' in sitem:
            if sitem['service_icon']:
                print sitem['service_icon']
                icon_content = ServiceIcon.objects(id=ObjectId(item['service_icon']))
                if len(icon_content) > 0:
                    sitem['service_icon'] = icon_content[0]['icon_b64']
                    sitem['service_icon_format'] = icon_content[0]['icon_format']
        provider_id = sitem['provider']
        if provider_id:
            provider = get_db(_cfg.database__database_name)['users'].find_one({'_id': ObjectId(provider_id)})
            sitem['provider'] = item_to_json(provider, ['_id', 'user_name'])
        return sitem

    def _get_items(self, skip=0, limit=1000, **values):
        return super(ServicesRes, self)._get_items(skip, limit, dict(activated=True))

    def get(self):
        return super(ServicesRes, self).get()


class ServicesProviderRes(ItemRes):
    collection = 'services'
    _cls = AppService
    name = 'Services'
    fields = '_id,created_at,name,summary,service_type,provider,context,sectors,price_initial,price_x_hour,activated'.split(
        ',')

    @get_exists_user(None)
    @get_authorize('User.Provider', 'services', False, 'provider', True)
    def get(self, id):
        limit = get_int(get_arg('limit'))
        skip = get_int(get_arg('skip'))
        _filter = dict(provider=ObjectId(id))
        result = super(ServicesProviderRes, self)._get_items(skip=skip * limit, limit=limit, values=_filter)
        js_items = [self.item_to_json(item) for item in result]
        response = dict(count=count_collection(self.collection, _filter), skip=skip, limit=limit,
                        result=js_items)
        return respond_json(response, status=200)

    def item_to_json(self, item):
        js_item = {}
        for field in self.fields:
            data = item.get(field)

            if isinstance(data, ObjectId):
                js_data = unicode(data)

            elif isinstance(data, datetime):
                # js_data = str(data)
                js_data = data.isoformat()
            elif isinstance(data, dict):
                js_data = None
                js_sub_data = {}
                for i in data:
                    if isinstance(data[i], ObjectId):
                        js_sub_data[i] = str(data[i])
                    else:
                        js_sub_data[i] = data[i]

                js_item[field] = js_sub_data
            else:
                js_data = data
            if js_data is not None:
                js_item[field] = js_data
        return js_item


class ServiceRes(ItemRes):
    collection = 'services'
    _cls = AppService
    name = 'Service'
    fields = '_id,name,summary,description,service_type,provider,sectors,keywords,link,' \
             'created_at,created_by,updated_at,updated_by,price_initial,price_x_hour'.split(',')

    def _item_to_json(self, item):
        sitem = ItemRes._item_to_json(self, item)
        provider_id = sitem['provider']
        if provider_id:
            provider = get_db(_cfg.database__database_name)['users'].find_one({'_id': ObjectId(provider_id)})
            sitem['provider'] = item_to_json(provider, ['_id', 'user_name'])
        return sitem

    def get(self,id):
        return super(ServiceRes, self).get(id)

    @get_exists_user(None)
    @get_authorize('User.Provider', 'services', True, 'provider')
    def put(self,id):
        return super(ServiceRes, self).put(id)


class ServiceTypesRes(Resource):
    def get(self):
        return [dict(name=st[0], description=st[1][1]) for st in get_service_types()]


class VMImageRes(Resource):
    @get_exists_user('User.Provider')
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
            response = dict(status='nok', msg="Error")
            return respond_json(response, status=400)


class ServiceConsumerParamsRes(ColRes):
    @get_exists_user(None)
    @get_authorize(None, 'services', True, 'provider')
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
    @get_exists_user('User.Provider')
    def post(self):
        _file = request.files['file']
        filename = secure_filename(_file.filename)
        _file.save(os.path.join(_cfg.repository__download, filename))


class VMImageUnchunkedRes(Resource):
    @get_exists_user('User.Provider')
    def post(self):
        data = get_json()
        filename_uuid = '{0}.img'.format(str(uuid.uuid4()))
        filename = '{0}{1}'.format(_cfg.repository__download, filename_uuid)
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
                response = dict(md5="ok", name_image=data['filename'],
                                filename_uuid=filename_uuid)
                return respond_json(response, status=200)
            else:
                # Devolvemos 409
                response = dict(status="nok", msg="Error to upload file. MD5 not equal")
                return respond_json(response, status=409)
        except Exception as e:
            self.delete_files_tmp(path_repository, filename)
            response = dict(status="nok", msg="Error to upload file")
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
    @get_exists_user('User.Provider')
    def post(self):
        data = get_json()
        try:
            vm_image = VMImage(data['filename'])
            data_vm = vm_image.save_image_2(data['filename_uuid'])
            os.remove(_cfg.repository__download + data['filename_uuid'])
            response = dict(vm_image=unicode(data_vm), name_image=data['filename'])
            return respond_json(response, status=200)
        except Exception as e:
            os.remove(_cfg.repository__download + data['filename'])
            response = dict(status="nok", msg="Error to upload file")
            return respond_json(response, status=500)

class Flavors(ItemRes):
    @get_exists_user(None)
    def get(self, id):
        orch = Orchestrator(debug=False)
        return orch.get_flavors(id)


class Pop(ItemRes):
    @get_exists_user(None)
    def get(self):
        orch = Orchestrator(debug=False)
        return orch.get_pop()
