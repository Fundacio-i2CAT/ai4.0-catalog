# -*- coding: utf-8 -*-

from datetime import datetime

from mongoengine import *
from mongoengine import signals

from anella.common import get_user
from user import User

class Base(Document):
    created_at = DateTimeField(required=True)
    created_by = StringField()
    updated_at = DateTimeField()
    updated_by = StringField()

    meta = {'allow_inheritance': True}

#     def save(self, *args, **kwargs):
#         pre_save(self.__class__, self)
#         return super(Base, self).save(self, *args, **kwargs)

class PreSave(object):

    def __init__(self):
        pass

    def send(self, cls, document, **kwargs):
        if not isinstance(document, Base):
            return
        user = get_user()
        if getattr(document, 'created_at', None)==None:
            document.created_at = datetime.now()
            document.created_by = user.user_name if user else ''

        document.updated_at = datetime.now()
        document.updated_by = user.user_name if user else ''

        if not document.pk:
            pass


signals.pre_save = PreSave()

