#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Service Icon Model"""

from mongoengine import StringField
from mongoengine import Document, DateTimeField
import datetime

class ServiceIcon(Document):
    """Stores service icons in base64 encoding"""

    timestamp = DateTimeField(default=datetime.datetime.now)
    icon_b64 = StringField(required=True)
