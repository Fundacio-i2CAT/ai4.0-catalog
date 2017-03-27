#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Service Manager Mailer"""

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import yaml
import json

CFG_FILENAME = 'prod-config.yaml'

class ServiceManagerMailer(object):
    """Represents a service manager mailer"""

    def __init__(self):
        with open(CFG_FILENAME) as fhandle:
            cfg = yaml.load(fhandle)
        self.cfg = cfg['anella']['mail']
        self.template = {}
        with open(self.cfg['ban']) as stream:
            self.template['ban'] = stream.read()
        with open(self.cfg['welcome']) as stream:
            self.template['welcome'] = stream.read()
        with open(self.cfg['notify']) as stream:
            self.template['notify'] = stream.read()
        with open(self.cfg['account']) as stream:
             jsontext = stream.read()
             data = json.loads(jsontext)
             self.cfg['smtp'] = data['smtp']
             self.cfg['pass'] = data['pass']
             self.cfg['port'] = data['port']

    def ban(self, toaddr):
        self.send_email(toaddr, self.cfg['system'], 'Usuari desactivat',
                        self.template['ban'].format(toaddr, self.cfg['system']))

    def welcome(self, toaddr):
        self.send_email(toaddr, self.cfg['system'], 'Usuari activat',
                        self.template['welcome'].format(toaddr, self.cfg['system']))

    def notify(self, toaddr):
        self.send_email(self.cfg['owner'], self.cfg['system'],
                        'Nou usuari registrat',
                        self.template['notify'].format(toaddr))

    def send_email(self, toaddr, fromaddr, subject, body):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['To'] = toaddr
        msg['From'] = fromaddr
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(self.cfg['smtp'], self.cfg['port'])
        server.starttls()
        server.login(fromaddr, self.cfg['pass'])
        server.sendmail(msg.get('From'), msg['To'], msg.as_string())
        server.quit()
        server.close()


    def __repr__(self):
        return self.template['ban']


if __name__ == '__main__':
    SMM = ServiceManagerMailer()
    SMM.ban('alfonso.egio@i2cat.net')
    print "SMM: ", SMM
