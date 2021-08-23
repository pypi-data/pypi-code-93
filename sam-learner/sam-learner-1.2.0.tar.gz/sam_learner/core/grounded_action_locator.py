"""Locates actions and grounds them according to the input data."""
from typing import List, Tuple

from pddl.pddl import Action, Domain

from sam_learner.sam_models.parameter_binding import ParameterBinding


def parse_plan_action_string(action_str: str) -> Tuple[str, List[str]]:
	"""Parse the action string and returns its name and parameters.

	:param action_str: the string representing the action. should look like:
	 	(load-truck obj23 tru2 pos2)
	:return: the action's name and it's arguments.
	"""
	action_data = action_str.strip("()").split(" ")
	action_name = action_data[0]
	action_params = action_data[1:]
	if action_params == [""]:
		action_params = []

	return action_name, action_params


def locate_lifted_action(domain: Domain, action_name: str) -> Action:
	"""Locate the input action in the domain.

	:param domain: the problem domain that is being used.
	:param action_name: the name of the action to locate.
	:return: the action object in the domain.
	"""
	try:
		return domain.actions[action_name]

	except KeyError:
		raise ValueError("Action not found in the domain!")


def ground_lifted_action(action: Action, parameters_values: List[str]) -> Tuple[
	Action, List[ParameterBinding]]:
	"""Locate the action's parameters and binds them to grounded values.

	:param action: the action to be grounded.
	:param parameters_values: the values of the action's parameters found in the plan data.
	:return: The action and it's parameters binding.
	"""
	binding = []
	for param_value, action_param in zip(parameters_values, action.signature):
		parameter_name, types = action_param
		binding.append(ParameterBinding(parameter_name, types, param_value))

	return action, binding
