# coding=utf-8
from anella.api.utils import get_token
from functools import wraps
import jwt
from bson.objectid import ObjectId
from anella.api.utils import respond_json, decode_token, \
    create_message_error, find_one_in_collection, count_collection
from anella.model.user import Provider, Client, User
from anella.common import get_view_args

role_user = {'User.Client': Client,
             'User.Provider': Provider}


def authorizate(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        jwt_token = get_token()
        if jwt_token:
            try:
                jwt.decode(jwt_token, 'secret',
                           algorithms=['HS256'])
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return respond_json(create_message_error(403, 'TOKEN_EXPIRED'),
                                    status=403)
        return fn(*args, **kwargs)
    return decorated_view


'''
Tanto proveedores como clientes lo pueden ver.
Comprobamos que el usuario exista
'''


def get_exists_user():
    def security(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            try:
                decode_jwt = decode_token(get_token())
                if decode_jwt:
                    data = find_one_in_collection('users', {"_id": ObjectId(decode_jwt['user_id']),
                                                            "activated": True})
                    if data is None:
                        return return_error_response(401, 'NO_AUTORIZED')
                else:
                    return return_error_response(403, 'TOKEN_EXPIRED')
                return fn(*args, **kwargs)
            except Exception:
                return return_error_response(403, '')

        return decorated

    return security


'''
Tienen acceso algun tipo de usuarios (Proveedor o cliente)
miramos collección y atributo a consultar
    model: es proveedor o cliente
    is_by_id: en la búsqueda de proyecto, es necesario buscar por el campo "_id"
    attribute: campo por el que se ha de buscar
    is_same_user: Si se ha de realizar la comprobación de id de la url i el id del token
'''


def get_authorize(model, collection, is_by_id, attribute, is_same_user=False):
    def security(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            try:
                decode_jwt = decode_token(get_token())
                if decode_jwt:
                    if is_same_user:
                        if get_http_status_code(ObjectId(decode_jwt['user_id']), ObjectId(get_view_args())) == 401:
                            return return_error_response(401, 'NO_AUTORIZED')
                    if get_http_status_code(get_model(model), get_model(decode_jwt['role'])) == 401:
                        return return_error_response(401, 'NO_AUTORIZED')
                    if is_by_id:
                        filters = {"_id": ObjectId(get_view_args()),
                                   attribute: ObjectId(decode_jwt['user_id'])}
                    else:
                        filters = {attribute: ObjectId(decode_jwt['user_id'])}
                    data = find_one_in_collection(collection, filters)
                    if data is None:
                        return return_error_response(401, 'NO_AUTORIZED')
            except Exception:
                return return_error_response(403, '')
            return fn(*args, **kwargs)

        return decorated

    return security


'''
    model: es proveedor o cliente
    is_by_id: en la búsqueda de proyecto, es necesario buscar por el campo "_id"
    attribute: campo por el que se ha de buscar
    is_same_user: Si se ha de realizar la comprobación de id de la url i el id del token
'''


def get_authorize_projects(model, is_by_id=True, attribute=None, is_same_user=False):
    def security(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            try:
                decode_jwt = decode_token(get_token())
                if decode_jwt:
                    if is_same_user:
                        if get_http_status_code(ObjectId(decode_jwt['user_id']), ObjectId(get_view_args())) == 401:
                            return return_error_response(401, 'NO_AUTORIZED')
                    user_model = model
                    if model is None:
                        user_model = get_model(decode_jwt['role'])
                    if user_model == Client:
                        data = get_project('projects', get_filter(is_by_id, decode_jwt, attribute))
                        if data is None:
                            return return_error_response(401, 'NO_AUTORIZED')
                    elif user_model == Provider and not is_same_user:
                        data = get_project('projects', {"_id": ObjectId(get_view_args())})
                        if data is None:
                            return return_error_response(401, 'NO_AUTORIZED')
                        is_sproject = False
                        for sprojects in data['services']:
                            item = get_project('sprojects', {"_id": sprojects,
                                                             "provider": ObjectId(decode_jwt['user_id'])})
                            if item is not None:
                                is_sproject = True
                                break
                        if not is_sproject:
                            return return_error_response(401, 'NO_AUTORIZED')
            except Exception:
                return return_error_response(403, '')
            return fn(*args, **kwargs)
        return decorated
    return security

'''
def get_after_authorized(model):
    def security(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            funct = fn(*args, **kwargs)
            if funct['status'] != 200:
                return respond_json(funct, funct['status'])
            response = []
            decode_jwt = decode_token(get_token())
            user_model = get_model(decode_jwt['role'])
            if get_http_status_code(ObjectId(decode_jwt['user_id']), ObjectId(get_view_args())) == 401:
                return return_error_response(401, 'NO_AUTORIZED')
            if get_http_status_code(get_model(model), get_model(decode_jwt['role'])) == 401:
                return return_error_response(401, 'NO_AUTORIZED')
            if user_model == Provider:
                for item in funct['response']['result']:
                    if item['provider'] == decode_jwt['user_id']:
                        response.append(item)
                funct['response']['result'] = response
                funct['response']['count'] = count_collection('sprojects',
                                                              {'provider': ObjectId(decode_jwt['user_id'])})
            return funct
        return decorated
    return security
'''


def get_project(collection, filter):
    return find_one_in_collection(collection, filter)


def return_error_response(status_code, msg):
    return respond_json(create_message_error(status_code, msg),
                        status=status_code)


def get_filter(is_by_id, decode_jwt, attribute=None):
    if is_by_id:
        filters = {"_id": ObjectId(get_view_args()), "client": ObjectId(decode_jwt['user_id'])}
    else:
        filters = {attribute: ObjectId(decode_jwt['user_id'])}
    return filters


def get_http_status_code(a, b):
    if a == b:
        return 200
    else:
        return 401


def get_role_user(user_id):
    u = User()
    return u.get(dict(_id=ObjectId(user_id)))


def get_model(model):
    return role_user.get(model)
