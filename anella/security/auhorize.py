from functools import wraps
import jwt
from anella.api.utils import respond_json, create_message_error
from anella.common import get_view_args
from anella.api.utils import get_token, decode_token, count_collection, find_in_collection
from anella.model.user import Provider, Client, User
from bson.objectid import ObjectId

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
                return respond_json(dict(message='TOKEN_EXPIRED'), status=403)
        return fn(*args, **kwargs)

    return decorated_view


def get_permission(model):
    def security(fn):
        @wraps(fn)
        def decorated_url(*args, **kwargs):
            try:
                decode_jwt = decode_token(get_token())
                _model = get_model(decode_jwt, model)
                if get_authorize(_model, role_user.get(decode_jwt['role'])) == 401:
                    return respond_json(create_message_error(401, 'NO_AUTORIZED'), status=401)
                if get_authorize(ObjectId(decode_jwt['user_id']), ObjectId(get_view_args())) == 401:
                    return respond_json(create_message_error(401, 'NO_AUTORIZED'), status=401)
                return fn(*args, **kwargs)
            except Exception:
                return respond_json(create_message_error(403, ''), status=403)
        return decorated_url
    return security


def after_get_permission(model):
    def security(fn):
        @wraps(fn)
        def decorated_url(*args, **kwargs):
            field = None
            r = fn(*args, **kwargs)
            decode_jwt = decode_token(get_token())
            _model = get_model(decode_jwt, model)
            if get_authorize(_model, role_user.get(decode_jwt['role'])) == 401:
                return respond_json(create_message_error(401, 'NO_AUTORIZED'), status=401)
            if _model == Client:
                field = r['client']
            elif _model == Provider:
                field = r['provider']
            return get_authorize_data(decode_jwt, field, r)
        return decorated_url
    return security


def after_function(fn):
    @wraps(fn)
    def post_function(*args, **kwargs):
        r = fn(*args, **kwargs)
        if r['status'] != 200:
            return respond_json(r, r['status'])
        decode_jwt = decode_token(get_token())
        role = role_user.get(decode_jwt['role'])
        if role == Client:
            ''' hemos de buscar los proyectos de los clientes,
            si tiene acceso al servicio que solicitan '''
            id_client = ObjectId(decode_jwt['user_id'])
            search_filter = dict(client=id_client)
            cursor = find_in_collection("projects", search_filter)
            is_service = False
            for item in cursor:
                search_filter = dict(project=item['_id'], service=ObjectId(get_view_args()))
                sprojects = count_collection("sprojects", search_filter)
                if sprojects > 0:
                    is_service = True
                    break
            if not is_service:
                return respond_json(create_message_error(401, 'NO_AUTORIZED'), status=401)
        elif role == Provider:
            if get_authorize(ObjectId(decode_jwt['user_id']), ObjectId(r['provider'])) == 401:
                return respond_json(create_message_error(401, 'NO_AUTORIZED'), status=401)
        else:
            return respond_json(create_message_error(403, ''), status=403)
        return r['response']
    return post_function


def get_authorize(a, b):
    if a == b:
        return 200
    else:
        return 401


def get_role_user(user_id):
    u = User()
    return u.get(dict(_id=ObjectId(user_id)))


def get_model(decode_jwt, model):
    if model is None:
        # Tiene acceso tanto cliente como Proveedor
        user = get_role_user(decode_jwt['user_id'])
        model = role_user.get(user['_cls'])
    return model


def get_authorize_data(decode_jwt, field, function):
    if decode_jwt['user_id'] not in field:
        return respond_json(create_message_error(401, 'NO_AUTORIZED'), status=401)
    return function['response']
