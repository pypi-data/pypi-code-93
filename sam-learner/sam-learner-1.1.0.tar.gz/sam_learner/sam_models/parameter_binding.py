"""represent a biding between a parameter and its respected object / other parameter name."""
from typing import Tuple

from pddl.pddl import Type


class ParameterBinding:
	"""Class representing the binding between a parameter and its respected objects."""

	parameter_name: str
	parameter_types: Tuple[Type]
	grounded_object: str

	def __init__(self, name: str, types: Tuple[Type], grounded_object: str):
		self.parameter_name = name
		self.parameter_types = types
		self.grounded_object = grounded_object

	def __str__(self):
		return f"('{self.grounded_object}', {self.parameter_types[0]})"

	def __repr__(self):
		return f"parameter - {self.parameter_name} with the types - {self.parameter_types} " \
			   f"contains the grounded object - {self.grounded_object}"

	def __eq__(self, other):
		return (self.parameter_name == other.parameter_name
				and str(self.parameter_types) == str(other.parameter_types)
				and self.grounded_object == other.grounded_object)

	def bind_parameter(self) -> Tuple[str, Type]:
		"""Bind the predicate's signature to the relevant object.

		:return: the grounded predicate signature.
		"""
		return self.grounded_object, self.parameter_types[0]
