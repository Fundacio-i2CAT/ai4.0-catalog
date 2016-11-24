# -*- coding: utf-8 -*-

import os

from anella.common import *
from anella.api.utils import respond_json
from anella.model.service import get_service_cls, get_service_types
from anella.model.service import AppService, VMImage
from anella import configuration as _cfg
from anella.model.service import create_service
from flask import request

from anella.api.utils import ColRes, ItemRes, Resource, item_to_json, ObjectId

class ServicesRes(ColRes):
    collection= 'services'
    _cls = AppService
    name= 'Services'
    fields = '_id,name,summary,service_type,provider,sectors,created_at,updated_at'.split(',')
    filter_fields = 'name,keywords,sectors'.split(',')

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
            provider = get_db(_cfg.database__database_name)['partners'].find_one({'_id':ObjectId(provider_id)})
            sitem['provider'] = item_to_json(provider, ['_id', 'name'])
        return sitem

class ServiceRes(ItemRes):
    collection= 'services'
    _cls = AppService
    name= 'Service'
    fields = '_id,name,summary,description,service_type,provider,sectors,keywords,link,created_at,created_by,updated_at,updated_by'.split(',')

    def _item_to_json(self, item):
        sitem = ItemRes._item_to_json(self, item)
        provider_id = sitem['provider']
        if provider_id:
            provider = get_db(_cfg.database__database_name)['partners'].find_one({'_id':ObjectId(provider_id)})
            sitem['provider'] = item_to_json(provider, ['_id', 'name'])
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

