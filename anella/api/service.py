
import json
import os
import time

from anella.common import *
from anella.model.service import ServiceDescription

def services():
#     import pdb;pdb.set_trace()
#     get_connection()

#     with open('services.json', 'r') as f:
#         services = json.loads(f.read())

    if get_method() == 'POST':
        attrs = get_fields()
        new_service = ServiceDesciption(**attrs)
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

def service(service_id):
#     import pdb;pdb.set_trace()
#     get_connection()

#     with open('services.json', 'r') as f:
#         services = json.loads(f.read())


    try:
        service = ServiceDescription.objects(pk=service_id)
        if service is None:
            response = dict( count=0, status='fail', 
                             msg='service not found',
                             result=[] )
       
            return respond_json( json.dumps(response), status=404)

        if request.method == 'DEL':
            service.delete()
            response = dict( count=0, status='ok', 
                             msg='service deleted',
                             result=[] )
       
        response = dict( count=1, status='ok', 
                         msg='service desciption',
                         result=[service,] )
        return respond_json( json.dumps(response))

    except Exception, e:
        return error_api( msg=str(e) )


