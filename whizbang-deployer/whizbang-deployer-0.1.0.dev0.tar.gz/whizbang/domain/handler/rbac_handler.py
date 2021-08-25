from abc import abstractmethod

from whizbang.config.app_config import AppConfig
from whizbang.domain.handler.handler_base import IHandler, HandlerBase
from whizbang.domain.manager.az.az_rbac_manager import IAzRbacManager
from whizbang.domain.models.rbac_policy import RBACPolicy
from whizbang.util.json_helpers import import_local_json
from whizbang.util.path_defaults import get_solution_directory
from whizbang.util.path_helpers import find_file


class IRbacHandler(IHandler):
    """"""

    @abstractmethod
    def set_rbac(self, solution_name, resource_ids: dict):
        """"""


class RbacHandler(HandlerBase, IRbacHandler):
    def __init__(self, app_config: AppConfig, rbac_manager: IAzRbacManager):
        HandlerBase.__init__(self, app_config=app_config)
        self.__rbac_manager = rbac_manager

    def set_rbac(self, solution_name, resource_ids: dict):

        solution_directory = get_solution_directory(self._app_config, solution_name)
        file_path = find_file('rbac_policies.json', solution_directory)
        if file_path is None:
            print('no rbac_policies.json found, skip setting rbac policies')
            return

        rbac_list = import_local_json(file_path)
        rbac_policies: 'list[RBACPolicy]' = []
        for policy in rbac_list:
            scope_name = policy['scope_name']
            scope = resource_ids[scope_name]

            if policy['assignee'] in resource_ids:
                assignee = resource_ids[policy['assignee']].split('/')[-1]
            else:
                assignee = policy['assignee']

            role = policy['role']
            assignee_type = policy['assignee_type']

            rbac_policy = RBACPolicy(scope=scope, assignee=assignee, role=role, assignee_type=assignee_type)
            rbac_policies.append(rbac_policy)

        result = self.__rbac_manager.assign_resource_roles(rbac_policies)
