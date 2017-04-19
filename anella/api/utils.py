# -*- coding: utf-8 -*-

from datetime import datetime
from mongoengine import *
from mongoengine import ValidationError, NotUniqueError
from bson import ObjectId, DBRef
from flask import json, jsonify, make_response
from flask_restful import Resource
from anella.common import *
from anella import configuration as _cfg
import re
import jwt


class AnellaRes(Resource):
    _cls = None
    collection = ''
    fields = ''
    name = ''

    TIMEOUT = 1000

    def _item_to_json(self, item):
        return item_to_json(item, self.fields)

    def _items_to_json(self, items):
        if not items:
            return []
        js_items = [self._item_to_json(item) for item in items]
        return js_items

    def _item_from_json(self, data, fields=None, cls=None):
        return item_from_json(data, self._cls, fields=self.fields)

    def _items_from_json(self, data):
        if not data:
            return []
        items = [self._item_from_json(dat) for dat in data]
        return items

    def _find_item(self, id):
        return get_db(_cfg.database__database_name)[self.collection].find_one({'_id': ObjectId(id)})

    def _obj_from_json(self, data, obj=None):
        return obj_from_json(data, cls=self._cls, obj=obj)

    def _find_obj(self, id):
        try:
            obj = self._cls.objects.get(id=ObjectId(id))
            return obj
            # return self._cls.objects.get(pk=id)
        except DoesNotExist, e:
            pass

    def _validate(self, obj):
        try:
            obj.validate()
        except ValidationError, e:
            return str(e)


class ColRes(AnellaRes):
    filter_fields = ''
    LIMIT = 1000

    def _filter_from_inputs(self, values):
        filter = {}
        for name, value in values.items():
            if name not in self.filter_fields:
                raise KeyError("Parameter '%s' not in filters." % name)
            field = self._cls._fields.get(name)
            if isinstance(field, (ReferenceField, GenericReferenceField)):
                filter[name] = ObjectId(value)

            elif isinstance(field, (ListField,)) and \
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
                return error_api(msg='%s: %s' % (self.name, valid_error))

            obj.save()
            id = obj.pk
            if not id:
                return error_api(msg='%s insert error' % self.name, )

            response = dict(status='ok', id=unicode(id))
            return respond_json(response, status=201)
        except Exception, e:
            return error_api(msg=str(e))

    def _get_items(self, skip=0, limit=1000, values={}, order_by="created_at"):
        cursor = get_db(_cfg.database__database_name)[self.collection].find(values, skip=skip, limit=limit) \
            .sort(order_by, -1)
        return [self._item_to_json(item) for item in cursor]

    def get(self):
        try:
            values = get_args().copy()  # args are inmutable
            skip = int(values and values.pop('skip', 0) or 0)
            limit = int(values and values.pop('limit', 0) or self.LIMIT - skip)
            items = self._get_items(skip=skip, limit=limit)
            result = self._items_to_json(items)
            response = dict(status='ok', count=len(items), skip=skip, limit=limit,
                            msg='Items list' if items
                            else 'No items available',
                            result=result)
            return respond_json(response, status=200)
            # return response

        except Exception, e:
            return error_api(unicode(e))


class ItemRes(AnellaRes):
    def delete(self, id):
        try:
            result = get_db(_cfg.database__database_name)[self.collection].delete_one({'_id': ObjectId(id)})
            # v2 result = get_db()[self.collection].find_and_modify({'_id':ObjectId(id)}, remove=True)
            if result.deleted_count:
                response = dict(status='ok', msg='%s deleted' % self.name)
                return respond_json(response, status=200)

            return error_api(msg='%s not deleted' % self.name, status=404)

        except Exception, e:
            return error_api(msg=str(e), status=404)

    def put(self, id):
        try:
            data = dict(get_json())
            resp = regex_name(data)
            if resp is not None: return resp
            item = get_db(_cfg.database__database_name)[self.collection]. \
                update_one({'_id': ObjectId(id)},
                           {'$set': data}, upsert=False)
            if item.matched_count == 1:
                response = respond_json(dict(id=id, message="Updated correctly"))
            else:
                response = respond_json(dict(id=id, message="Not updated"), status=404)
            return response

        except Exception, e:
            return respond_json(dict(id=id, message=str(e)), status=404)

    def get(self, id):
        item = self._find_item(id)
        if not item:
            return error_api(msg='%s not found' % self.name, status=404)

        data = self._item_to_json(item)
        return data

    def _get_items(self, skip=0, limit=1000, values={}, order_by="created_at"):
        cursor = get_db(_cfg.database__database_name)[self.collection].find(values, skip=skip, limit=limit) \
            .sort(order_by, -1)
        return [item for item in cursor]


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

        js_item[field] = js_data
    return js_item


def item_from_json(data, cls, fields=None):
    cls = cls
    fields = fields or cls._fields.keys()
    item = {}
    for name in fields:
        field = cls._fields.get(name)
        if name not in data:
            continue
        value = data.get(name)
        if isinstance(field, (ReferenceField, GenericReferenceField)):
            item[name] = ObjectId(value)

        elif isinstance(field, (ListField,)) and \
                isinstance(field.field, (ReferenceField, GenericReferenceField)):
            item[name] = [ObjectId(val) for val in value]

        elif isinstance(field, (DateTimeField,)):
            item[name] = field.to_mongo(value)

        else:
            item[name] = value

    return item


def obj_from_json(data, cls, obj=None):
    item = item_from_json(data, cls)
    if obj is None:
        # obj = cls(**item)
        obj = cls()

    for name, value in item.items():
        field = cls._fields.get(name)
        if isinstance(field, (ReferenceField, GenericReferenceField)):
            obj[name] = DBRef(cls._get_collection_name(), value)

        elif isinstance(field, EmbeddedDocumentField):
            if obj[name]:
                obj[name] = obj_from_json(value, cls=field.document_type,
                                          obj=obj[name])
            else:
                obj[name] = obj_from_json(value, cls=field.document_type)

        elif isinstance(field, (ListField,)) and \
                isinstance(field.field, (ReferenceField, GenericReferenceField)):
            obj[name] = [DBRef(cls._get_collection_name(), val) for val in value]
        else:
            setattr(obj, name, value)

    return obj


def update_status_project(id, status):
    get_db(_cfg.database__database_name)['sprojects']. \
        update_one({'_id': ObjectId(id)},
                   {'$set': {'status': status}}, upsert=False)


def respond_json(data, status=200, **kwargs):
    headers = {
        'Cache-Control': 'no-cache',
        #             'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
    }
    if 'headers' in kwargs:
        for k, v in kwargs['headers']:
            headers[k] = v
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
    response = dict(status='fail', msg=msg)
    return respond_json(response, status=status)


def create_response(status_code, data):
    return respond_json(data, status=status_code)


def create_response_data(data):
    if data.status_code in (200, 201):
        return json.loads(data.text)
    else:
        return respond_json(data.text, status=data.status_code)


def get_token():
    return get_request().headers.get('authorization', None)


def decode_token(jwt_token):
    return jwt.decode(jwt_token, 'secret')


def count_collection(collection, values):
    return get_db(_cfg.database__database_name)[collection].find(values).count()


def find_one_in_collection(collection, values):
    return get_db(_cfg.database__database_name)[collection].find_one(values)


def find_in_collection(collection, filter):
    return get_db(_cfg.database__database_name)[collection].find(filter)


def get_int(variable):
    _i = 0
    if variable is not None: _i = int(variable)
    return _i


def create_message_error(status_code, code=None, status=""):
    data = get_db(_cfg.database__database_name)['errors'].find_one({'code': code})
    if data is None:
        data = {"i18n": {"ca": "S'ha produït un error inesperat",
                         "es": "Se ha producido un error inesperado"}}
    response = dict(status_code=status_code, code=code, message=data['i18n'], status=status)
    return response


def read_json_file(path):
    with open(path) as json_data:
        d = json.load(json_data)
        return d


def post(session, url, data, json_data):
    return session.post(url, headers=data, json=json_data)


def delete(session, url, data):
    return session.delete(url, headers=data)


def replace_characters(data, a, b):
    return data.replace(a, b)


def get_keystone_token(response):
    return response.headers.get('X-Subject-Token')


def create_keystone_headers(token):
    return {'X-Auth-Token': token,
            'Content-Type': 'application/json'}


def regex_name(item):
    response = None
    if 'name' in item:
        if re.search('[¿?<>º"!·$%&/()=]', item['name']):
            msg = create_message_error(400, 'NAME_INVALID')
            response = respond_json(msg, status=400)
    return response
