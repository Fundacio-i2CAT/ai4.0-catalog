# -*- coding: utf-8 -*-

from datetime import datetime

from mongoengine import *
from mongoengine import signals

from anella.common import get_user
from user import User

class Base(object):
    created_at = DateTimeField(required=True)
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
            document.created_at = datetime.now()
            document.created_by = user.user_name if user else ''

        document.updated_at = datetime.now()
        document.updated_by = user.user_name if user else ''

        if not document.pk:
            pass


signals.pre_save = PreSave()

class WithLogo(object):
    """
    A document with a logo attached.
    """
    logo = FileField()

