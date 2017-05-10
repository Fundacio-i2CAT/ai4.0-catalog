#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Service Icon Model"""

from mongoengine import StringField
from mongoengine import Document, DateTimeField
import datetime
import imghdr,StringIO


class ServiceIcon(Document):
    """Stores service icons in base64 encoding"""

    timestamp = DateTimeField(default=datetime.datetime.now)
    icon_b64 = StringField(required=True)
    icon_format = StringField(required=True)

def guess_format(icon_b64):
    gformat = imghdr.what(StringIO.StringIO(icon_b64.decode('base64')))
    if gformat:
        return gformat
    else:
        return 'unknown'
