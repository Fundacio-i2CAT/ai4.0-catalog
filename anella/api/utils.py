# -*- coding: utf-8 -*-

import os
import time
from collections import Iterable
from datetime import datetime

from mongoengine import *
from mongoengine import ValidationError, NotUniqueError
from bson import ObjectId

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
        js_item = {}
        for field in self.fields:
           data = item.get(field)
           if isinstance(data, Document):
               js_data = { 'oid' : unicode(data.pk), '_cls': data.__class__.__name__ }
 
           elif isinstance(data, ObjectId):
               js_data = unicode(data)

           elif isinstance(data, datetime):
               js_data = str(data)
 
           else:
               js_data = data

           js_item[field]= js_data

        return js_item
    

    def _items_to_json(self, items):
        if not items:
            return []
        js_items= [ self._item_to_json(item) for item in items]
        return js_items

    def _item_from_json(self, data):
        item ={}
        for name in self.fields:
            field = self._cls._fields.get(name)
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

    def _items_from_json(self, data):
        if not data:
            return []
        items= [ self._item_from_json(dat) for dat in data]
        return items

    def _find_item(self, id):
        # ME services = ServiceDescription.objects(pk=service_id)
        item = get_db()[self.collection].find_one({'_id':ObjectId(id)})
        if item:
            return self._item_to_json(item)

    def _obj_from_json(self, data, obj=None):
        item = self._item_from_json(data)
        if obj is None:
            obj = self._cls(**item)
        else:
            for n,v in item.items():
                setattr(obj, n, v)
        return obj

    def _find_obj(self, id):
        try:
            return self._cls.objects.get(pk=id)
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
        for name in self.filter_fields:
            field = self._cls._fields.get(name)
            if name not in values:
                continue
            value = values.get(name)
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
            # item = self._item_from_json(data)
            # result = get_db()[self.collection].insert_one( item )
            # # v2. result = get_db()[self.collection].save( item )
            # id = result.inserted_id

            # Using ME validation
            # import pdb;pdb.set_trace()
            obj = self._obj_from_json(data)
            valid_error = self._validate(obj)
            if valid_error:
                response = dict( status='fail', msg='%s: %s' % (self.name,valid_error))
                return respond_json( response, status=400)
            obj.save()
            id = obj.pk

            if not id:
                response = dict( status='fail', msg='%s insert error' % self.name,)
                return respond_json( response, status=400)

            response = dict( status='ok', id=unicode(id))
            return respond_json( response, status=201)
        except Exception,e:
            return error_api( msg=str(e) )

    def get(self):
        try:
            values = get_args()
            filter = self._filter_from_inputs(values)
            skip = values and values.get('skip') or 0
            limit = values and values.get('limit') or self.LIMIT-skip
            cursor = get_db()[self.collection].find( filter, skip=skip, limit=limit )
            items = [item for item in cursor ]

            response = dict( status='ok', count=len(items), skip=skip, limit=limit,
                             msg='Items list' if items 
                                              else 'No items available',
                             result=self._items_to_json(items) )
            return respond_json( response, status=200)
            # return response
    
        except Exception, e:
            return error_api( str(e) )

class IdRes(AnellaRes):
  
    def delete(self, id):
        try:
            result = get_db()[self.collection].delete_one({'_id':ObjectId(id)})
            # v2 result = get_db()[self.collection].find_and_modify({'_id':ObjectId(id)}, remove=True)
            if result.deleted_count:
                response = dict( status='ok', msg='%s deleted' % self.name )
                return respond_json( response, status=200)
           
            response = dict( status='fail', msg='%s not deleted' % self.name,)
            return respond_json( response, status=404)

        except Exception,e:
            return error_api( msg=str(e) )
           
    def put(self, id):
        try:
            data = get_json()
            item = self._item_from_json(data)
            result = get_db()[self.collection].update_one({'_id':ObjectId(id)}, 
                                                          {'$set' :item } )
            # v2 get_db()[self.collection].update({'_id':ObjectId(id)}, {'$set': item } )
            if not result.matched_count:
                response = dict( status='fail', msg='%s not updated' % self.name,)
                return respond_json( response, status=400)

            # Validation
            # import pdb;pdb.set_trace()
            # obj = self._find_obj(id)
            # item = self._find_item(id)
            # item.update(self._item_from_json(data))
            # obj = self._obj_from_json(item) #(data, obj)
            # valid_error = self._validate(obj)
            # if valid_error:
            #     response = dict( status='fail', msg='%s: %s' % (self.name,valid_error))
            #     return respond_json( response, status=400)

            # obj.save()

            response = dict( status='ok', msg='%s updated' % self.name )
            return respond_json( response, status=200)

        except Exception,e:
            return error_api( msg=str(e) )
    
    def get(self, id):
        item = self._find_item(id)
        if not item:
            response = dict( status='fail', msg='%s not found' % self.name,)
            return respond_json( response, status=404)

        data = self._item_to_json(item)
        return data

class ImageRes(Resource):
    _cls=None
    collection=''
    field=''
    name=''

    def post(self, id):
        item = self._find_item(id)
        if not item:
            response = dict( status='fail', msg='%s not found' % self.name,)
            return respond_json( response, status=404)

        data = self._item_to_json(item)
        return data

def respond_json(data, status=200, **kwargs):

    headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
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

def error_api(msg):
    response = dict( count=0, status='fail', msg=msg, result=[])
    return respond_json( json.dumps(response), status=500,)


