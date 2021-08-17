"""Extract the effects from the state based on the exclusion and inclusion rules."""
from typing import Tuple, List

from pddl.pddl import Predicate

from sam_learner.sam_models.comparable_predicate import ComparablePredicate
from sam_learner.sam_models.state import State


def extract_effects(
		previous_state: State, next_state: State) -> Tuple[List[Predicate], List[Predicate]]:
	"""Extract the effects of the action according to the two lemmas that we know.

	:param previous_state: the state that had been before the action was executed.
	:param next_state: the state after the action was executed.
	:return: the add effects and the del effects.
	"""
	prev_state_predicates = set([ComparablePredicate(predicate=predicate) for predicate in
								 previous_state.facts])
	next_state_predicates = set([ComparablePredicate(predicate=predicate) for predicate in
								 next_state.facts])
	add_effects = next_state_predicates.difference(prev_state_predicates)
	del_effects = prev_state_predicates.difference(next_state_predicates)
	return list(add_effects), list(del_effects)
