# -*- coding: utf-8 -*-

import os
import time
from collections import Iterable
from datetime import datetime

from mongoengine import *
from mongoengine import ValidationError, NotUniqueError
from bson import ObjectId, DBRef

from flask import json, jsonify, make_response
from flask_restful  import Resource

from anella.common import *

class AnellaRes(Resource):
    _cls=None
    collection=''
    fields=''
    name=''

    TIMEOUT = 1000

    def _item_to_json(self, item):
        return item_to_json(item, self.fields)

    def _items_to_json(self, items):
        if not items:
            return []
        js_items= [ self._item_to_json(item) for item in items]
        return js_items

    def _item_from_json(self, data, fields=None, cls=None):
        return item_from_json(data, self._cls, fields=self.fields)

    def _items_from_json(self, data):
        if not data:
            return []
        items= [ self._item_from_json(dat) for dat in data]
        return items

    def _find_item(self, id):
        return get_db()[self.collection].find_one({'_id':ObjectId(id)})

    def _obj_from_json(self, data, obj=None):
        return obj_from_json(data, cls=self._cls, obj=obj)

    def _find_obj(self, id):
        try:
            obj = self._cls.objects.get(id=ObjectId(id))
            return obj
            # return self._cls.objects.get(pk=id)
        except DoesNotExist,e:
            pass

    def _validate(self, obj):
        try:
            obj.validate()
        except ValidationError,e:
            return str(e)

class ColRes(AnellaRes):
    filter_fields=''
    LIMIT = 1000

    def _filter_from_inputs(self, values):
        filter ={}
        for name,value in values.items():
            if name not in self.filter_fields:
                raise KeyError("Parameter '%s' not in filters." % name)

            field = self._cls._fields.get(name)
            if isinstance(field, (ReferenceField, GenericReferenceField)):
                filter[name] = ObjectId(value)

            elif isinstance(field, (ListField, )) and \
                 isinstance(field.field, (ReferenceField, GenericReferenceField)):
                filter[name] = [ObjectId(val) for val in value]

            else:
                filter[name] = value

        return filter

    def post(self):
        try:
            data = get_json()
            # Using ME validation
            obj = self._obj_from_json(data)
            valid_error = self._validate(obj)
            if valid_error:
                return error_api(msg='%s: %s' % (self.name,valid_error))

            obj.save()
            id = obj.pk
            if not id:
                return error_api( msg='%s insert error' % self.name,)

            response = dict( status='ok', id=unicode(id))
            return respond_json( response, status=201)
        except Exception,e:
            return error_api( msg=str(e) )

    def _get_items(self, skip=0, limit=1000):
        values = get_args().copy() # args are inmutable
        filter = self._filter_from_inputs(values)
        cursor = get_db()[self.collection].find( filter, skip=skip, limit=limit )
        return [item for item in cursor ]

    def get(self):
        try:
            values = get_args().copy() # args are inmutable
            skip = int(values and values.pop('skip', 0) or 0)
            limit = int(values and values.pop('limit', 0) or self.LIMIT-skip)
            items = self._get_items(skip=skip, limit=limit)
            result=self._items_to_json(items)
            response = dict( status='ok', count=len(items), skip=skip, limit=limit,
                             msg='Items list' if items 
                                              else 'No items available',
                             result=result )
            return respond_json( response, status=200)
            # return response
    
        except Exception, e:
            return error_api( unicode(e) )

class ItemRes(AnellaRes):
  
    def delete(self, id):
        try:
            result = get_db()[self.collection].delete_one({'_id':ObjectId(id)})
            # v2 result = get_db()[self.collection].find_and_modify({'_id':ObjectId(id)}, remove=True)
            if result.deleted_count:
                response = dict( status='ok', msg='%s deleted' % self.name )
                return respond_json( response, status=200)
           
            return error_api(msg='%s not deleted' % self.name, status=404)

        except Exception,e:
            return error_api( msg=str(e), status=404 )
           
    def put(self, id):
        try:
            data = get_json()
            # item = self._item_from_json(data)
            # result = get_db()[self.collection].update_one({'_id':ObjectId(id)}, 
            #                                               {'$set' :item } )
            # # v2 get_db()[self.collection].update({'_id':ObjectId(id)}, {'$set': item } )
            # if not result.matched_count:
            #     response = dict( status='fail', msg='%s not updated' % self.name,)
            #     return respond_json( response, status=400)

            # ME Validation
            obj = self._find_obj(id)
            obj = self._obj_from_json(data, obj)
            valid_error = self._validate(obj)
            if valid_error:
                return error_api( msg='%s: %s' % (self.name,valid_error))

            obj.save()

            response = dict( status='ok', msg='%s updated' % self.name )
            return respond_json( response, status=200)

        except Exception,e:
            return error_api( msg=str(e) )
    
    def get(self, id):
        item = self._find_item(id)
        if not item:
            return error_api( msg='%s not found' % self.name, status=404)

        data = self._item_to_json(item)
        return data

def item_to_json(item, fields):
    js_item = {}
    for field in fields:
       data = item.get(field)

       if isinstance(data, ObjectId):
           js_data = unicode(data)

       elif isinstance(data, datetime):
           # js_data = str(data)
           js_data = data.isoformat()

       else:
           js_data = data

       js_item[field]= js_data

    return js_item

def item_from_json(data, cls, fields=None):
    cls = cls
    fields = fields or cls._fields.keys()
    item ={}
    for name in fields:
        field = cls._fields.get(name)
        if name not in data:
            continue
        value = data.get(name)
        if isinstance(field, (ReferenceField, GenericReferenceField)):
            item[name] = ObjectId(value)

        elif isinstance(field, (ListField, )) and \
             isinstance(field.field, (ReferenceField, GenericReferenceField)):
            item[name] = [ObjectId(val) for val in value]

        elif isinstance(field, (DateTimeField, )):
            item[name] = field.to_mongo(value)

        else:
            item[name] = value

    return item

def obj_from_json(data, cls, obj=None):
    item = item_from_json(data, cls )
    if obj is None:
        # obj = cls(**item)
        obj = cls()

    for name,value in item.items():
        field = cls._fields.get(name)
        if isinstance(field, (ReferenceField, GenericReferenceField)):
            obj[name] = DBRef(cls._get_collection_name(), value)

        elif isinstance(field, EmbeddedDocumentField):
            if obj[name]:
                obj[name] = obj_from_json(value, cls=field.document_type, 
                                          obj=obj[name])
            else:
                obj[name] = obj_from_json(value, cls=field.document_type )

        elif isinstance(field, (ListField, )) and \
             isinstance(field.field, (ReferenceField, GenericReferenceField)):
            obj[name] = [DBRef(cls._get_collection_name(), val) for val in value]
        else:
            setattr(obj, name, value)

    return obj

def respond_json(data, status=200, **kwargs):

    headers={
            'Cache-Control': 'no-cache',
#             'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
            }
    if 'headers' in kwargs:
        for k,v in kwargs['headers']:
            headers[k]=v
        del kwargs['headers']

    if not isinstance(data, basestring):
        data = json.dumps(data)

    resp = make_response(data, str(status))
    resp.headers.extend(headers)
    return resp


def not_found_api():
    from flask import abort
    abort(405)

def error_api(msg, status=400):
    response = dict( status='fail', msg=msg)
    return respond_json( response, status=status)


