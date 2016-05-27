from mongoengine import connect
from mongoengine.connection import get_db

from anella.model.user import User

_connection = None
_db = None
_user = None

def get_connection():
    global _connection

    if _connection is None:
        _connection = connect(db='mongoenginetest')

    return _connection

# def get_db():
#     global _db
# 
#     if _db is None:
#         get_connection()
#         _db = get_db()
# 
#     return _db

def get_user():
    global _user

    if _user is None:
        get_db()
        users = User.objects(user_name='orambla')
        if not users:
            _user = User('orambla@gmail.com')
            _user.save()
        else:
            _user = users[0]

    return _user

