
import json
import os
import time

from anella.common import *
from anella.model.service import get_service_type, get_service_type, ServiceDescription, SERVICE_TYPES

def service_from_json(data):
    result = json.loads(data)
    service_cls = get_service_cls( result['service_type'] )
    return service_cls.from_json(data)

def services():
    if get_method() == 'POST':
        try:
            data = get_data()
            new_service = service_from_json(data)
            new_service.save()
        except Exception,e:
            return error_api( msg=str(e) )

    try:
        services = [service.to_json() for service in ServiceDescription.objects()]
        response = dict( count=len(services), status='ok', 
                         msg='Services list' if services 
                                             else 'No services available',
                         result=services )
        return respond_json( json.dumps(response))

    except Exception, e:
        return error_api( str(e) )

def service(service_id):
#     get_connection()

#     with open('services.json', 'r') as f:
#         services = json.loads(f.read())


    try:
        service = ServiceDescription.objects(pk=service_id)
        if service is None:
            response = dict( count=0, status='fail', 
                             msg='Service not found',
                             result=[] )
       
            return respond_json( json.dumps(response), status=404)

        service = service[0]
        if get_method() == 'DELETE':
            try:
                service.delete()
                response = dict( count=0, status='ok', 
                                 msg='Service deleted',
                                 result=[] )
                return respond_json( json.dumps(response))
            except Exception,e:
                return error_api( msg=str(e) )
       
        if get_method() == 'POST':
            try:
                data = get_data()
                service = service_from_json(data)
                service.save()
                data = service.to_json()
                response = dict( count=0, status='ok', 
                             msg='Service updated',
                             result=[data,] )
                return respond_json( json.dumps(response))
            except Exception,e:
                return error_api( msg=str(e) )

        data = service.to_json()
        response = dict( count=1, status='ok', 
                         msg='Service description',
                         result=[data,] )
        return respond_json( json.dumps(response))

    except Exception, e:
        return error_api( msg=str(e) )


