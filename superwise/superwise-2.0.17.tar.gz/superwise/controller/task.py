""" This module implement tasks functionality  """
from superwise.controller.base import BaseController


class TaskController(BaseController):
    """Class TaskController - responsible for task functionality"""

    def __init__(self, client, sw):
        """
        Constructor of TaskController class
        """
        super().__init__(client, sw)
        self.path = "admin/v1/tasks"
        self.model_name = "Task"

    def create_segment(self, task_id, name, definition):
        params = {"name": name, "definition": definition}

        url = self.build_url("admin/v1/task/{}/segment".format(task_id))
        res = self.client.post(url, params)
        res.raise_for_status()
        return res.content
