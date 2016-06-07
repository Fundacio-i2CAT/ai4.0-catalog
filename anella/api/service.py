# -*- coding: utf-8 -*-

import json
import os
import time

from anella.common import *
from anella.model.service import get_service_type, get_service_cls, GenericService, SERVICE_TYPES

from anella.api.utils import ColRes, IdRes

class ServicesRes(ColRes):
    collection= 'services'
    _cls = GenericService
    name= 'Services'
    fields = '_id,name,summary,service_type,provider,sectors,created_at,updated_at'.split(',')
    filter_fields = 'name,keywords,sectors'.split(',')

    def item_from_json(self, data):
        service_cls = get_service_cls( data.get('service_type') )
        if service_cls:
            self._cls = service_cls
        item = ColRes.item_from_json(self, data)
        item['_cls'] = service_cls._class_name
        # obj = service_cls.from_json(item)
        return item

class ServiceRes(IdRes):
    collection= 'services'
    _cls = GenericService
    name= 'Service'
    fields = '_id,name,summary,description,service_type,provider,sectors,keywords,link,created_at,created_by,updated_at,updated_by'.split(',')


