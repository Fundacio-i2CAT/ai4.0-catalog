from functools import wraps
import jwt
from anella.api.utils import respond_json, create_message_error
from anella.common import get_path, get_view_args
from anella.api.utils import get_token
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
                jwt_token = get_token()
                decode_jwt = jwt.decode(jwt_token, 'secret')
                _model = model
                if model is None:
                    #Tiene acceso tanto cliente como Proveedor
                    user = get_role_user(decode_jwt['user_id'])
                    _model = role_user.get(user['_cls'])
                if get_authorize(_model, role_user.get(decode_jwt['role'])) == 401:
                    return respond_json(create_message_error(401, 'NO_AUTORIZED'), status=401)
                if get_authorize(ObjectId(decode_jwt['user_id']), ObjectId(get_view_args())) == 401:
                    return respond_json(create_message_error(401, 'NO_AUTORIZED'), status=401)
                return fn(*args, **kwargs)
            except Exception:
                return respond_json(create_message_error(403, ''), status=403)
        return decorated_url
    return security


def get_authorize(a, b):
    if a == b:
        return 200
    else:
        return 401

def get_role_user(user_id):
    u = User()
    return u.get(dict(_id=ObjectId(user_id)))


