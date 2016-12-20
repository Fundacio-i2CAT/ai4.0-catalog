from anella.common import get_json, get_session

from anella.api.utils import ItemRes, respond_json, error_api
from anella.api.user import UserRes
from anella.auth import Authenticator


class SessionRes(ItemRes):
    def __init__(self):
        self.auth = Authenticator()

    def post(self):
        item = get_json()
        return respond_json('', status=self.auth.user_login(item['user_name'], item['password']))
    
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

