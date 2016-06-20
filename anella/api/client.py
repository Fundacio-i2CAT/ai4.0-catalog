# -*- coding: utf-8 -*-

import json
import os
import time

from flask_restful import reqparse, abort, Resource

from anella.common import *
from anella.model.partner import Client

from anella.api.utils import ColRes, ItemRes
from anella.api.service import ServicesRes, GenericService

class ClientsRes(ColRes):
    collection= 'partners'
    _cls = Client
    name= 'Clients'
    fields = '_id,name,summary,link,contact,partner_type,sectors,created_at,updated_at'.split(',')
    filter_fields = 'name,sectors'.split(',')

    def _filter_from_inputs(self, values):
        filter = super(ClientsRes, self)._filter_from_inputs(values)
        filter['_cls'] = 'Partner.Client'
        return filter

class ClientRes(ItemRes):
    collection= 'partners'
    _cls = Client
    name= 'Client'
    fields = '_id,name,summary,description,link,contact,partner_type,sectors,created_at,created_by,updated_at,updated_by'.split(',')

