"""Matches predicates to their corresponding actions based on the common types."""
import copy
import logging
from typing import NoReturn, List, Tuple, Optional

from pddl.parser import Parser
from pddl.pddl import Type, Domain

from sam_learner.sam_models.comparable_predicate import ComparablePredicate
from sam_learner.sam_models.grounded_action import GroundedAction


def validate_no_duplicates(tested_list: List[str]) -> NoReturn:
	"""Validate that the predicate has only one possible match in the literal.

	:param tested_list: the list to test for duplicates.
	"""
	contains_duplicates = len(set(tested_list)) != len(tested_list)
	if contains_duplicates:
		raise ValueError(f"No duplications allowed! The predicates received - {tested_list}")


class PredicatesMatcher:
	"""Class that matches predicates according to the needed properties in the learning process."""

	learned_domain: Domain
	logger: logging.Logger

	def __init__(self, domain_path: Optional[str] = None, domain: Optional[Domain] = None):
		self.logger = logging.getLogger(__name__)
		assert not (domain_path and domain)
		if domain_path is not None:
			self.learned_domain = Parser(domain_path).parse_domain(read_from_file=True)

		if domain is not None:
			self.learned_domain = domain

	def match_predicate_to_action_literals(
			self, grounded_predicate: ComparablePredicate,
			grounded_signature: List[Tuple[str, Tuple[Type]]],
			lifted_signature: List[Tuple[str, Tuple[Type]]]) -> Optional[ComparablePredicate]:
		"""Match a literal to a possible lifted precondition for the input action.

		:param grounded_predicate: the grounded predicate that represent part of the previous state.
		:param grounded_signature: the signature of the action that contains the actual objects
			that the action was executed on.
		:param lifted_signature: the lifted signature of the action, is accessible from the
			trajectory.
		:return: a precondition, in case the action and the predicate contain matching objects,
			None otherwise.
		"""
		predicate_objects = [signature_item[0] for signature_item in grounded_predicate.signature]
		grounded_action_objects = [signature_item[0] for signature_item in grounded_signature]
		validate_no_duplicates(predicate_objects)
		validate_no_duplicates(grounded_action_objects)

		if not set(predicate_objects).issubset(set(grounded_action_objects)):
			return None

		domain_predicate = self.learned_domain.predicates[grounded_predicate.name]
		possible_precondition: ComparablePredicate = ComparablePredicate(
			domain_predicate.name, domain_predicate.signature)
		for index, (action_object_name, object_types) in enumerate(grounded_signature):
			if action_object_name not in predicate_objects:
				continue

			literal_object_index = predicate_objects.index(action_object_name)
			parameter_name, parameter_types = lifted_signature[index]
			possible_precondition.signature[literal_object_index] = (
				parameter_name, parameter_types)

		return possible_precondition

	def get_possible_literal_matches(self, grounded_action: GroundedAction,
									 literals: List[ComparablePredicate]) -> List[ComparablePredicate]:
		"""Get a list of possible preconditions for the action according to the previous state.

		:param grounded_action: the grounded action that was executed according to the trajectory.
		:param literals: the list of literals that we try to match according to the action.
		:return: a list of possible preconditions for the action that is being executed.
		"""
		possible_matches = []
		lifted_signature = grounded_action.lifted_signature
		grounded_signature = grounded_action.grounded_signature
		for predicate in literals:
			try:
				matches = self.match_predicate_to_action_literals(
					predicate, grounded_signature, lifted_signature)

			except ValueError as error:
				self.logger.debug(f"When parsing {grounded_action.activated_action_representation}, "
								  f"with the predicate {str(predicate)} "
								  f"got the error {error}! proceeding!")
				matches = None

			if matches is None:
				continue

			possible_matches.append(copy.deepcopy(matches))

		return possible_matches
