# -*- coding: utf-8 -*-

from datetime import datetime

from mongoengine import *
from mongoengine import signals

from anella.common import get_user

class Base(object):
    created_at = DateTimeField()
    created_by = StringField()
    updated_at = DateTimeField()
    updated_by = StringField()

class PreSave(object):

    def __init__(self):
        pass

    def send(self, cls, document, **kwargs):
        if not isinstance(document, Base):
            return
        user = get_user()
        if getattr(document, 'created_at', None)==None:
            document.created_at = datetime.utcnow()
            document.created_by = user.user_name if user else ''
            document.updated_at = None
            document.updated_by = None

        else:
            document.updated_at = datetime.utcnow()
            document.updated_by = user.user_name if user else ''

        if not document.pk:
            pass


signals.pre_save = PreSave()
