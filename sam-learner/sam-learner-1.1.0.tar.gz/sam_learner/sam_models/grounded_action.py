"""module that represents a grounded action and its data."""
from pddl.pddl import Action, Type
from typing import List, Tuple

from sam_learner.sam_models.parameter_binding import ParameterBinding


class GroundedAction:
	"""Grounded action with bindings that represent the actual objects the action is applied on."""

	action: Action
	parameter_bindings: List[ParameterBinding]

	def __init__(self, action: Action, bindings: List[ParameterBinding]):
		self.action = action
		self.parameter_bindings = bindings

	@property
	def activated_action_representation(self) -> str:
		"""The signature of the grounded operator in the form of - (action o1 o2 o3 ... on)"""
		grounded_parameters = " ".join(
			[binding.grounded_object for binding in self.parameter_bindings])
		return f"({self.action.name} {grounded_parameters})"

	@property
	def grounded_signature(self) -> List[Tuple[str, Tuple[Type]]]:
		return [(binding.grounded_object, binding.parameter_types) for binding in
				self.parameter_bindings]

	@property
	def lifted_action_name(self) -> str:
		return self.action.name

	@property
	def lifted_signature(self) -> List[Tuple[str, Tuple[Type]]]:
		return self.action.signature
