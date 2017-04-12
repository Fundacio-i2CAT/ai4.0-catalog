# -*- coding: utf-8 -*-

from anella.api.utils import ColRes
from anella.common import get_json
from anella.model.register import Register


class RegisterRes(ColRes):
    def __init__(self):
        self.register = Register()

    def post(self):
        item = get_json()
        return self.register.save_keystone(item)
