from anella.common import get_json, get_session

from anella.api.utils import ItemRes, respond_json, error_api
from anella.api.user import UserRes
from anella.auth import Authenticator
from anella.model.user import User


class SessionRes(ItemRes):
    def __init__(self):
        self.auth = Authenticator()

    def post(self):
        try:
            data = get_json()
            if 'user_name' in data:
                user = User.objects.get(user_name=data['user_name'])
            elif 'email' in data:
                user = User.objects.get(email=data['email'])
            else:
                error_api("Missing email,user_name.", status=400)

            if user.has_password(data['password']):
                get_session()['user'] = unicode(user.pk)
                # item = get_db()['users'].find_one({'_id':user.pk})
                # item = UserRes()._item_to_json(item)
                session_id = get_session().sid
                response = dict(status='ok', user_id=unicode(user.pk), session_id=session_id,
                                msg="Welcomed '%s'." % user.user_name)
                return respond_json(response, status=200)

            response = dict(status='fail', msg="Wrong password.")
            return respond_json(response, status=400)
        except Exception, e:
            response = dict(status='fail', msg=unicode(e))
            return respond_json(response, status=400)

    '''EURECAT
    def post(self):
        item = get_json()
        status_code = self.auth.user_login(item['user_name'], item['password'])
        if status_code == 200:
            #login correct
            return respond_json(dict(msg='ok'), status=status_code)
        else:
            #login incorrect
            return respond_json(dict(msg='nok'), status=status_code)
    '''
    def delete(self):
        try:
            del get_session()['user']
            response = dict( status='ok', msg="Signed out.")
            return respond_json( response, status=200)
        except KeyError,e:
            response = dict( status='fail', msg="Not signed in.")
            return respond_json( response, status=400)

class SessionUserRes(UserRes):

    def get(self):
        if get_session() and get_session().get('user'):
            return UserRes.get(self, get_session().get('user'))
        else:
            error_api("Not signed in.", status=404)

