# -*- coding: utf-8 -*-

import json
import os
import time

from anella.common import *
from anella.model.service import get_service_type, get_service_cls, get_service_types
from anella.model.service import AppService, ISService

from anella.api.utils import ColRes, ItemRes, Resource, item_to_json, ObjectId

class ServicesRes(ColRes):
    collection= 'services'
    _cls = AppService
    name= 'Services'
    fields = '_id,name,summary,service_type,provider,sectors,created_at,updated_at'.split(',')
    filter_fields = 'name,keywords,sectors'.split(',')

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
            provider = get_db()['partners'].find_one({'_id':ObjectId(provider_id)})
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
            provider = get_db()['partners'].find_one({'_id':ObjectId(provider_id)})
            sitem['provider'] = item_to_json(provider, ['_id', 'name'])
        return sitem


class ServiceTypesRes(Resource):

    def get(self):
        return [ dict(name=st[0], description=st[1][1]) for st in get_service_types()]

