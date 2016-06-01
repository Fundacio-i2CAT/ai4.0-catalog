
import json
import os
import time

from anella.common import *
from anella.model.project import ServiceContext, Project

def projects():
#     import pdb;pdb.set_trace()
#     get_connection()

#     with open('services.json', 'r') as f:
#         services = json.loads(f.read())

    if get_method() == 'POST':
        attrs = get_fields()
        new_service = Projct(**attrs)
        # new_service['id'] = int(time.time() * 1000)
        try:
            new_service.save()
        except Exception,e:
            return error_api( msg=str(e) )

    try:
        services = [service for service in ServiceDescription.objects()]
        response = dict( count=len(services), status='ok', 
                         msg='services list' if services 
                                             else 'no services available',
                         result=services )
        return respond_json( json.dumps(response))

    except Exception, e:
        return error_api( str(e) )

def project(project_id):
#     import pdb;pdb.set_trace()
#     get_connection()

#     with open('projects.json', 'r') as f:
#         projects = json.loads(f.read())


    try:
        project = Project.objects(pk=project_id)
        if project is None:
            response = dict( count=0, status='fail', 
                             msg='project not found',
                             result=[] )
       
            return respond_json( json.dumps(response), status=404)

        if get_method() == 'DEL':
            project.delete()
            response = dict( count=0, status='ok', 
                             msg='project deleted',
                             result=[] )
       
        response = dict( count=1, status='ok', 
                         msg='project desciption',
                         result=[project,] )
        return respond_json( json.dumps(response))

    except Exception, e:
        return error_api( msg=str(e) )


