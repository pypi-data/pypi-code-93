"""This module exports the domain object to a domain file."""
from collections import defaultdict
from pathlib import Path
from typing import NoReturn, List, Dict

from pddl.pddl import Domain, Action, Predicate, Type


class DomainExporter:
	"""Class that is able to export a domain to a correct PDDL file."""

	def write_action_preconditions(self, predicates: List[Predicate]) -> str:
		"""Writes the predicates of an action's precondition according to the PDDL file format.

		:param predicates: the predicates that are in the domain's definition.
		:return: the formatted string representing the domain's predicates.
		"""
		formatted_preconditions = "{content}"
		if len(predicates) > 1:
			formatted_preconditions = "(and {content})"

		action_predicates = self._write_positive_predicates(predicates)
		return formatted_preconditions.format(content=" ".join(action_predicates))

	@staticmethod
	def _write_positive_predicates(predicates: List[Predicate]) -> List[str]:
		"""writes positive predicates according to the format of a PDDL file.

		:param predicates: the preconditions / effects of an action.
		:return: the formatted positive predicates.
		"""
		action_predicates = []
		for predicate in predicates:
			predicate_formatted_signature = " ".join([f"{name}" for name, _ in predicate.signature])
			predicate_str = f"({predicate.name} {predicate_formatted_signature})"
			action_predicates.append(predicate_str)

		return action_predicates

	@staticmethod
	def _write_negative_predicates(predicates: List[Predicate]) -> List[str]:
		"""writes negative predicates according to the format of a PDDL file.

		:param predicates: the preconditions / effects of an action.
		:return: the formatted negative predicates.
		"""
		action_predicates = []
		for predicate in predicates:
			predicate_formatted_signature = " ".join([f"{name}" for name, _ in predicate.signature])
			predicate_str = f"(not ({predicate.name} {predicate_formatted_signature}))"
			action_predicates.append(predicate_str)

		return action_predicates

	def write_action_effects(self, add_effects: List[Predicate], delete_effects: List[Predicate]) -> str:
		"""Write the effects of an action according to the PDDL file format.

		:param add_effects: the add effects of an action.
		:param delete_effects: the delete effects of an action.
		:return: the formatted string representing the action's effects.
		"""
		action_predicates = self._write_positive_predicates(add_effects)
		action_predicates + self._write_negative_predicates(delete_effects)
		formatted_effects = "{content}"
		if len(action_predicates) > 1:
			formatted_effects = "(and {content})"

		return formatted_effects.format(content=" ".join(action_predicates))

	def write_action(self, action: Action) -> str:
		"""Write the action formatted string from the action data.

		:param action: The action that needs to be formatted into a string.
		:return: the string format of the action.
		"""
		action_params = " ".join([f"{name} - {types[0]}" for name, types in action.signature])
		action_preconds = self.write_action_preconditions(action.precondition)
		action_effects = self.write_action_effects(action.effect.addlist, action.effect.dellist)
		return f"(:action {action.name}\n" \
			   f"\t:parameters   ({action_params})\n" \
			   f"\t:precondition {action_preconds}\n" \
			   f"\t:effect       {action_effects})\n" \
			   f"\n"

	@staticmethod
	def write_predicates(predicates: Dict[str, Predicate]) -> str:
		"""Writes the predicates formatted according to the domain file format.

		:param predicates: the predicates that are in the domain's definition.
		:return: the formatted string representing the domain's predicates.
		"""
		predicates_str = "(:predicates\n{predicates})\n\n"
		predicates_strings = []
		for predicate_name, predicate in predicates.items():
			predicate_params = " ".join(
				[f"{name} - {types[0]}" for name, types in predicate.signature])
			predicates_strings.append(f"\t({predicate_name} {predicate_params})")

		return predicates_str.format(predicates="\n".join(predicates_strings))

	def write_constants(self, constants: Dict[str, Type]) -> str:
		"""TODO: Complete this if there is a domain that contains constants."""
		pass

	@staticmethod
	def write_types(types: Dict[str, Type]) -> str:
		"""Writes the definitions of the types according to the PDDL file format.

		:param types: the types that are available in the learned domain.
		:return: the formatted string representing the types in the PDDL domain file.
		"""
		types_str = "(:types\n{types_content})\n"
		sorted_types = defaultdict(list)
		for type_name, pddl_type in types.items():
			if pddl_type.parent is not None:
				sorted_types[pddl_type.parent.name].append(type_name)
			else:
				continue

		types_content = []
		for pddl_type_name, sub_types in sorted_types.items():
			type_pddl_str = "\t"
			type_pddl_str += "\n\t".join([child_type for child_type in sub_types[:-1]])
			type_pddl_str += f"\n\t{sub_types[-1]} - {pddl_type_name}"
			types_content.append(type_pddl_str)

		return types_str.format(types_content="\n".join(types_content))

	def export_domain(self, domain: Domain, export_path: Path) -> NoReturn:
		"""Export the domain object to a correct PDDL file.

		:param domain: the learned domain object.
		:param export_path: the path to the file that the domain would be exported to.
		"""
		domain_types = self.write_types(domain.types)
		domain_headers = f"(define (domain {domain.name})\n" \
						 "(:requirements :strips :typing)\n\n" \
						 f"{domain_types}\n" \
						 "{domain_content})"
		domain_content = self.write_predicates(domain.predicates)
		for action in domain.actions.values():
			domain_content += self.write_action(action)

		with open(export_path, "wt") as export_domain_file:
			export_domain_file.write(domain_headers.format(domain_content=domain_content))
