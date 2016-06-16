# -*- coding: utf-8 -*-

import json
import os
import time

from flask_restful import reqparse, abort, Resource

from anella.common import *
from anella.model.partner import Provider, ANELLA_SECTORS, PARTNER_TYPES

from anella.api.utils import ColRes, ItemRes
from anella.api.service import ServicesRes, GenericService

class ProvidersRes(ColRes):
    collection= 'partners'
    _cls = Provider
    name= 'Providers'
    fields = '_id,name,summary,link,contact,sectors,created_at,updated_at'.split(',')
    filter_fields = 'name'.split(',')

    def _filter_from_inputs(self, values):
        filter = super(ProvidersRes, self)._filter_from_inputs(values)
        filter['_cls'] = 'Partner.Provider'
        return filter

class ProviderRes(ItemRes):
    collection= 'partners'
    _cls = Provider
    name= 'Provider'
    fields = '_id,name,summary,description,link,contact,sectors,created_at,created_by,updated_at,updated_by'.split(',')

class ProviderServicesRes(ServicesRes):
    collection= 'services'
    document_cls = GenericService
    name= 'Services'
    fields = '_id,name,summary,service_type,provider,sectors,link'.split(',')
    query_fields = 'name,keywords,sectors,link'.split(',')

    def item_from_json(self, item):
        return service_from_json(item)

    def get(self, provider_id):
        pass

class ProviderSectorsRes(Resource):
    def get(self):
        return [ dict(name=st[0], description=st[1]) for st in ANELLA_SECTORS]

class ProviderTypesRes(Resource):
    def get(self):
        return [ dict(name=st[0], description=st[1]) for st in PARTNER_TYPES]

