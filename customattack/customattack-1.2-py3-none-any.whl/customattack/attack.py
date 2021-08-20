
from collections import OrderedDict
from typing import List, Union

import customattack
# from customattack.attack_results import (
#     FailedAttackResult,
#     MaximizedAttackResult,
#     SkippedAttackResult,
#     SuccessfulAttackResult,
# )
from customattack.constraints import Constraint, PreTransformationConstraint
from customattack.goal_function_results import GoalFunctionResultStatus
from customattack.goal_functions import GoalFunction
from customattack.models.wrappers import ModelWrapper
from customattack.search_methods import SearchMethod
from customattack.shared import AttackedText, utils
from customattack.transformations import CompositeTransformation, Transformation

class Attack:
    def __init__(self):
    # def __init__(
    #     self,
    #     goal_function: GoalFunction,
    #     constraints: List[Union[Constraint, PreTransformationConstraint]],
    #     transformation: Transformation,
    #     search_method: SearchMethod,
    #     transformation_cache_size=2 ** 15,
    #     constraint_cache_size=2 ** 15,
    # ):
        print("settings")
