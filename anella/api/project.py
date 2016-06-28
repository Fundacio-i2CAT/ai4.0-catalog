# -*- coding: utf-8 -*-

from bson import ObjectId

from anella.common import *
from anella.model.project import Project, SProject

from anella.api.utils import ColRes, ItemRes, respond_json, error_api, item_to_json

def sprojects_to_json(sprojects):
    sitems=[]
    for service_id in sprojects:
        sproject = get_db()['sprojects'].find_one({'_id':service_id})
        sitem = item_to_json(sproject, ['context_type', 'status', 'provider'])
        service = get_db()['services'].find_one({'_id':sproject['service']})
        provider = get_db()['partners'].find_one({'_id':service['provider']})

        sitem['provider'] = item_to_json(provider, ['_id', 'name'])
        # sitem['service'] = item_to_json(service, ['_id', 'name'])
        sitem.update( item_to_json(service, ['_id', 'name']))
        sitems.append(sitem)

    return sitems

class ProjectsRes(ColRes):
    collection= 'projects'
    _cls = Project
    name= 'Projects'
    fields = '_id,name,summary,client,status,services,created_at,updated_at'.split(',')
    filter_fields = 'name,status'.split(',')

    def get(self):
        return ColRes.get(self)

    def _item_to_json(self, item):
        services = item.get('services')
        item['services'] = sprojects_to_json(services)
        return item_to_json(item, self.fields)

class ProjectRes(ItemRes):
    collection= 'projects'
    _cls = Project
    name= 'Project'
    fields = '_id,name,summary,description,client,services,status,created_at,created_by,updated_at,updated_by'.split(',')

    def _item_to_json(self, item):
        services = item.get('services')
        item['services'] = sprojects_to_json(services)
        return item_to_json(item, self.fields)

class ClientProjectsRes(ProjectsRes):

    def get(self, id):
        self.client_id=id
        return super(ClientProjectsRes, self).get()

    def _get_items(self, skip=0, limit=1000):
        values = get_args().copy() # args are inmutable
        # status = int(values and values.pop('status', 0)) or None
        filter = self._filter_from_inputs(values)
        filter['client'] = ObjectId(self.client_id)
        cursor = get_db()['projects'].find(filter, skip=skip, limit=limit )
        return [item for item in cursor ]

    def _filter_from_inputs(self, values):
        filter = super(ClientProjectsRes, self)._filter_from_inputs(values)
        filter['client'] = ObjectId(self.client_id)
        return filter

    def _item_to_json(self, item):
        services = item.get('services')
        item['services'] = sprojects_to_json(services)
        return item_to_json(item, self.fields)


class SessionProjectRes(ProjectRes):
    collection= 'projects'
    _cls = Project
    name= 'Project'
    fields = '_id,name,summary,description,client,status,created_at,created_by,updated_at,updated_by'.split(',')

    def post(self):
        if get_session() and get_session().get('user'):
            user = User.objects.get(id=get_session().get('user'))
        else:
            return error_api("Not signed in.", status=400)

        client = Client.objects.get(id=user.partner_id)
        if client is None:
            return error_api("User is not a client.", status=400)

        try:
            project = self._obj_from_json(get_json())
            project.client = client
            project.save()

            response = dict( status='ok', msg="Welcomed '%s'." % user.user_name )
            return respond_json( response, status=200)
    
            response = dict( status='fail', msg="Wrong password." )
            return respond_json( response, status=400)
        except Exception,e:
            response = dict( status='fail', msg=unicode(e) )
            return respond_json( response, status=400)
    


class ProjectServicesRes(ColRes):
    collection= 'sprojects'
    _cls = SProject
    name= 'Service Contract'
    fields = '_id,service,status,created_at,updated_at'.split(',')
#     filter_fields = 'name'.split(',')

    def post(self, id):
        try:
            project = Project.objects.get(id=ObjectId(id))
            obj = self._obj_from_json(get_json())
            obj.project = project
            valid_error = self._validate(obj)
            if valid_error:
                response = dict( status='fail', msg='%s: %s' % (self.name,valid_error))
                return respond_json( response, status=400)

            obj.save()
            response = dict( status='ok', msg='%s updated' % self.name )
            return respond_json( response, status=200)

        except Exception,e:
            return error_api( msg=str(e) )
        

class SProjectsRes(ColRes):
    collection= 'sprojects'
    _cls = SProject
    name= 'SProjects'
    fields = '_id,project,service,context'.split(',')

    def item_from_json(self, data):
        service_cls = get_service_cls( data.get('service_type') )
        if service_cls:
            self._cls = service_cls
        item = ColRes.item_from_json(self, data)
        item['_cls'] = service_cls._class_name
        # obj = service_cls.from_json(item)
        return item

class SProjectRes(ItemRes):
    collection= 'sprojects'
    _cls = SProject
    name= 'SProject'
    fields = 'project,service,context_type,context,status'.split(',')


class ProviderSProjectsRes(SProjectsRes):
    filter_fields = 'provider,status'.split(',')

    def get(self, id):
        self.provider_id=id
        return super(ProviderSProjectsRes, self).get()

    def _filter_from_inputs(self, values):
        filter = super(ProviderSProjectsRes, self)._filter_from_inputs(values)
        filter['provider'] = ObjectId(self.provider_id)
        return filter

    def _get_items(self, skip=0, limit=1000):
        values = get_args().copy() # args are inmutable
        # status = int(values and values.pop('status', 0)) or None
        filter = self._filter_from_inputs(values)
        filter['provider'] = ObjectId(self.provider_id)
        cursor = get_db()['sprojects'].find(filter, skip=skip, limit=limit )
        return [item for item in cursor ]

    def _items_to_json(self, items):
        return sprojects_to_json(items)
