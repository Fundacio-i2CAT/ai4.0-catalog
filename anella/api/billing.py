from anella.api.utils import ItemRes, find_one_in_collection, create_message_error, respond_json
from anella.model.project import Project
from anella.orch import Orchestrator
from bson import ObjectId
from anella.common import get_arg


class BillingRes(ItemRes):
    def __init__(self):
        self.project = Project()
        self.orch = Orchestrator()

    def get(self, id):
        self.project = find_one_in_collection(self.project.cls, {"_id": ObjectId(id)})
        sproject = find_one_in_collection('sprojects', {"project": self.project['_id']})
        instance = find_one_in_collection('instances', {"sproject": sproject["_id"]})
        if instance is not None:
            item = self.create_data(str(instance["instance_id"]))
            if item is None: return respond_json(create_message_error(400, "BAD_URL"), 400)
            data = self.orch.get_billing(item)
            status_code = data.status_code
            response = data.text
        else:
            response = create_message_error(404, "NO_INSTANCES")
            status_code = 404

        return respond_json(response, status=status_code)

    def create_data(self, instance_id):
        start_date = get_arg('start_date')
        end_date = get_arg('end_date')
        if start_date is None or start_date == ''\
                or end_date is None or end_date == '':
            return None
        return dict(instance=instance_id, start_date=start_date, end_date=end_date)
