#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Catalog db sanity check"""

from pymongo import MongoClient
from bson import ObjectId, DBRef
import sys
sys.path.insert(0, '~/catalog/')
from anella.model.project import STATES
import sys
import sys
import os
from termcolor import colored
from prettytable import PrettyTable
from hurry.filesize import size as fsize
from hurry.filesize import alternative
import os
import requests
import json

HARD = True

def get_projects_from_service(sid):
    projects = DB['projects'].find()
    service_projects = []
    service_sprojects = []
    for project in projects:
        for sproject_id in project['services']:
            sprojects = DB['sprojects'].find({'_id': ObjectId(sproject_id)})
            insflag = False
            for sproject in sprojects:
                if sproject['service'] == sid:
                    insflag = True
                    service_sprojects.append(sproject)
            if insflag:
                service_projects.append(project)
    return service_projects, service_sprojects

def service_resources(sid):
    pass

def check_services():
    services = DB['services'].find()
    table = PrettyTable(['n', 'name', 'p/sp', 'status', 'img', 'size'])
    table.align['name'] = 'l'
    table.align['n'] = 'r'
    table.align['status'] = 'l'
    table.align['img'] = 'l'
    table.align['size'] = 'r'
    service_selector = []
    for service in services:
        projects, sprojects = get_projects_from_service(service['_id'])
        psp = '({0}/{1})'.format(len(projects), len(sprojects))
        status = ''
        service_selector.append(service['_id'])
        for sproject in sprojects:
            if STATES[sproject['status']] == 'DISABLED':
                status = status+colored(STATES[sproject['status']][0:3]+' ', 'blue')
            elif STATES[sproject['status']] == 'CONFIRMED':
                status = status+colored(STATES[sproject['status']][0:3]+' ', 'green')
            elif STATES[sproject['status']] == 'DENIED':
                status = status+colored(STATES[sproject['status']][0:3]+' ', attrs=['reverse', 'blink'])
            elif STATES[sproject['status']] == 'RUNNING':
                status = status+colored(STATES[sproject['status']][0:3], 'red', attrs=['reverse', 'blink'])+' '
            elif STATES[sproject['status']] == 'DEPLOYED':
                status = status+colored(STATES[sproject['status']][0:3]+' ', 'white')
            else:
                status = status+STATES[sproject['status']][0:3]+' '
        if not 'vm_image' in service['context']:
            continue
        image = DBR['fs.files'].find({'_id': ObjectId(service['context']['vm_image'])})
        img = ''
        size = ''
        if image.count() < 1:
            if ( service['context']['vm_image_format'].upper() == 'openstack_id'.upper() ):
                img = img+colored('OSID', 'green')
            else:
                img = img+colored('NIMG', 'red')
        else:
            size = fsize(image[0]['length'], system=alternative)
            if ( service['context']['vm_image_format'].upper() == 'openstack_id'.upper() ):
                img = img+colored('OSID', 'green')
        table.add_row([len(service_selector)-1,
                       service['name'].encode('utf-8'),
                       psp,
                       status,
                       img,
                       size])
    print table
    return int(raw_input('Select service (clean all projects/sprojects from service): ')), service_selector

def get_projects_from_sproject(sid):
    projects = DB['projects'].find()
    response = []

    for project in projects:
        add = False
        for service in project['services']:
            if service == sid:
                add = True
        if add:
            response.append(project['_id'])
    return response

def clean_service(sid):
    projects, sprojects = get_projects_from_service(sid)
    for sproject in sprojects:
        instances = DB['instances'].find({'sproject': ObjectId(sproject['_id'])})
        clear_flag = True
        for instance in instances:
            url = '{0}/{1}'.format(ANELLA_PLUGIN, instance['instance_id'])
            response = requests.get(url)
            if response.status_code == 200 and not HARD:
                clear_flag = False
                data = json.loads(response.text)
            else:
                # DB['instances'].remove({'_id': ObjectId(instance['_id'])})
                print 'Going to delete {0}'.format(instance['instance_id'])
        if clear_flag:
            rprojects = get_projects_from_sproject(sproject['_id'])
            for project in rprojects:
                print 'GOing to delete {0}'.format(project)
                # DB['projects'].remove({'_id': ObjectId(project)})
            print 'gOing to delete {0}'.format(sproject['_id'])
            # DB['sprojects'].remove({'_id': ObjectId(sproject['_id'])})

if __name__ == '__main__':

    HOST = 'localhost'
    DBNAME = 'anella'
    DBRNAME = 'anella_repository'
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    if len(sys.argv) > 2:
        DBNAME = sys.argv[2]
    if len(sys.argv) > 3:
        DBRNAME = sys.argv[3]

    ANELLA_PLUGIN = 'http://{0}:8082/orchestrator/api/v0.1/service/instance'.format(HOST)
    CLIENT = MongoClient(host='mongodb://{0}:27017'.format(HOST))
    DB = CLIENT[DBNAME]
    DBR = CLIENT[DBRNAME]
    os.system('clear')
    selected, services = check_services()
    clean_service(services[selected])
    CLIENT.close()
