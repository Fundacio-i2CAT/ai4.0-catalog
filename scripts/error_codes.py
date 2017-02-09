#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Error codes script"""

from mongoengine import connect
from mongoengine import StringField
from mongoengine import Document, DictField
import json
import sys

class Errors(Document):
    """Error codes"""
    code = StringField(required=True, unique=True)
    i18n = DictField(required=True)

if __name__ == "__main__":
    print 'Please enter the database name [anella]: ',
    DATABASE_NAME = sys.stdin.readline().rstrip().lstrip()
    if len(DATABASE_NAME) < 1:
        DATABASE_NAME = 'anella'
    connect(db=DATABASE_NAME)
    with open('scripts/error_codes.json') as fhandle:
        ERROR_CODES = json.loads(fhandle.read())
    for ec in ERROR_CODES:
        error = Errors(code=ec['code'], i18n=ec['i18n'])
        try:
            error.save()
            print ec['code']+' inserted'
        except:
            print ec['code']+' was already in the collection'
