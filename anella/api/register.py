# -*- coding: utf-8 -*-

from anella.api.utils import Resource, ColRes, ItemRes, respond_json, error_api
from anella.common import *
from anella.model.register import *


class RegisterRes(ColRes):
    collection = 'register'
    _cls = Register
    name = 'Register'
    fields = '_id,email, name, surname, company, comp_position, legal, ' \
             'comp_address, comp_phone, password, client_role, provider_role, nif_cif, company'.split(',')
    filter_fields = 'name,'.split(',')

    def post(self):
        item = get_json()
        return create_register(item)
