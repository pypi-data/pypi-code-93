""" This module implement roles functionality  """
from superwise.controller.base import BaseController
from superwise.models.task import Task


class RoleController(BaseController):
    """ Role controller class, implement functionalitiws for roles API """

    def __init__(self, client, sw):
        """
        constructer for RoleController class

        :param client:

        """
        super().__init__(client, sw)
        self.path = "model/v1/roles"
        self.model_name = "Role"

    def get_by_task_type_id(self, task_type_id):
        """
        perform get task by type id call

        :param task_type_id: task type int
        :return model of task
        """
        self.logger.info("GET %s ", self.path)
        r = self.client.get(self.build_url("model/v1/task_type/{}/roles".format(task_type_id)))
        return self.parse_response(r)

    def list_to_dict(self, model_list):
        """
        change list of models into dict

        :param model_list: list of models
        :return dict
        """
        dict = {}
        for model in model_list:
            properties = model.get_properties()
            dict[properties["description"]] = properties
        return dict
