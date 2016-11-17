# -*- coding: utf-8 -*-

from gridfs import GridFS
from anella import configuration as _cfg

from flask_restful import Resource

from anella.common import *
from anella.model.partner import Provider, ANELLA_SECTORS, PARTNER_TYPES

from anella.api.utils import ColRes, ItemRes
from anella.api.service import ServicesRes, AppService
from bson.objectid import ObjectId

class ProvidersRes(ColRes):
    collection= 'partners'
    _cls = Provider
    name= 'Providers'
    fields = '_id,name,summary,link,contact,sectors,created_at,updated_at'.split(',')
    filter_fields = 'name,sectors'.split(',')

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
    document_cls = AppService
    name= 'Services'
    fields = '_id,name,summary,service_type,provider,sectors,link'.split(',')
    query_fields = 'name,keywords,sectors,link'.split(',')

    def item_from_json(self, item):
        return service_from_json(item)

    def get(self, provider_id):
        pass

class ProviderServicePublishRes(ItemRes):

    def get(self, id):
        grid_fs = GridFS(get_db(_cfg.database__database_repository))
        grid_fs_file = grid_fs.find_one({'_id': ObjectId(id)})
        file = open(_cfg.repository__path + grid_fs_file.name, 'w')
        file.write(grid_fs_file.read())
        file.close()
        return "ok"

class ProviderPostServicePublishRes(ItemRes):
    def post(self):
        grid_fs = GridFS(get_db(_cfg.database__database_repository))
        file = open("/home/david/Downloads/ubuntu-16.04-desktop-amd64.iso", 'r')
        file_id = grid_fs.put(file.read(), filename='ubuntu-16.04-desktop-amd64.iso')
        grid_fs_file = grid_fs.find_one(file_id)
        data = {"id": str(grid_fs_file._id)}
        grid_fs_file.close()
        return data


class PartnerSectorsRes(Resource):
    def get(self):
        return [ dict(name=st[0], description=st[1]) for st in ANELLA_SECTORS]

class PartnerTypesRes(Resource):
    def get(self):
        return [ dict(name=st[0], description=st[1]) for st in PARTNER_TYPES]

