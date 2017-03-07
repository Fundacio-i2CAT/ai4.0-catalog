from anella.api.utils import get_token
from functools import wraps
import jwt
from anella.api.utils import respond_json, create_message_error
from anella.common import get_path


def authorizate(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        jwt_token = get_token()
        print get_path()
        print
        if jwt_token:
            try:
                jwt.decode(jwt_token, 'secret',
                           algorithms=['HS256'])
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return respond_json(create_message_error(403,dict(message='TOKEN_EXPIRED')),
                                    status=403)
        elif get_path() != '/api/session':
            return respond_json(create_message_error(403,dict(message='TOKEN_EXPIRED')),
                                status=403)
        return fn(*args, **kwargs)
    return decorated_view