from abc import abstractmethod
from typing import List, Dict

from cloudrail.knowledge.context.gcp.gcp_environment_context import GcpEnvironmentContext
from cloudrail.knowledge.rules.base_rule import BaseRule, Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class GcpBaseRule(BaseRule[GcpEnvironmentContext]):

    @abstractmethod
    def execute(self, env_context: GcpEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        pass

    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def should_run_rule(self, environment_context: GcpEnvironmentContext) -> bool:
        pass

    def get_needed_parameters(self) -> List[ParameterType]:
        return []
