# -*- coding: utf-8 -*-

'''
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
'''
