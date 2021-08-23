"""This module is used to validate the correctness of the generated action model."""
from typing import Literal, Tuple, List

from pddl.pddl import Domain, Action

from sam_learner.sam_models.comparable_predicate import ComparablePredicate

ValidationType = Literal["precondition", "add-effect", "del-effect"]


def switch_comparisons_and_sort(expected_action: Action, generated_action: Action,
								validated_type: ValidationType) -> Tuple[List, List]:
	"""Creates the list of items to be compared and sorts them so that the comparison will be
	accurate.

	:param expected_action: the expected action that is in the complete domain.
	:param generated_action: the action that was learned using the learner algorithm.
	:param validated_type: the type of objects to compare.
	:return:
	"""
	if validated_type == "add-effect":
		generated_objects = generated_action.effect.addlist
		expected_objects = expected_action.effect.addlist
	elif validated_type == "precondition":
		generated_objects = generated_action.precondition
		expected_objects = expected_action.precondition
	else:
		generated_objects = generated_action.effect.dellist
		expected_objects = expected_action.effect.dellist

	generated_objects = [ComparablePredicate(predicate=pred) for pred in generated_objects]
	expected_objects = [ComparablePredicate(predicate=pred) for pred in expected_objects]
	generated_objects = sorted(generated_objects, key=lambda predicate: (predicate.name,
																		 str(predicate.signature)))
	expected_objects = sorted(expected_objects, key=lambda predicate: (predicate.name,
																	   str(predicate.signature)))
	return expected_objects, generated_objects


def validate_objects(generated_action: Action, expected_action: Action, validated_type: ValidationType) -> bool:
	"""Validate that the actions contain the same precondition / add effects / delete effects.

	:param generated_action: the action that was generated using the learning algorithm.
	:param expected_action: the actual action that is in the planning domain.
	:param validated_type: the type of object to test.
	:return: whether or not the items that were learned are the same.
	"""
	expected_objects, generated_objects = switch_comparisons_and_sort(
		expected_action, generated_action, validated_type)
	if len(generated_objects) == len(expected_objects) == 0:
		print(f"No {validated_type} in both the generated and the expected!")
		return True

	generated_textual = set([str(predicate) for predicate in generated_objects])
	expected_textual = set([str(predicate) for predicate in expected_objects])

	print(f"Generated {validated_type}: {generated_textual}")
	print(f"Expected {validated_type}: {expected_textual}")

	if len(generated_textual) != len(expected_textual):
		print(
			f"The length of the given objects does not match! Expected {len(expected_textual)} "
			f"but received {len(generated_textual)}")
		return False

	for generated_item, expected_item in zip(generated_objects, expected_objects):
		comparable_item = ComparablePredicate(predicate=generated_item)
		if comparable_item == expected_item:
			print(f"The {validated_type}s are either equal or the firsts if more precise.")
			return True

		return False


def validate_preconditions(generated_action: Action, expected_action: Action) -> bool:
	return validate_objects(generated_action, expected_action, "precondition")


def validate_add_effects(generated_action: Action, expected_action: Action) -> bool:
	return validate_objects(generated_action, expected_action, "add-effect")


def validate_delete_effects(generated_action: Action, expected_action: Action) -> bool:
	return validate_objects(generated_action, expected_action, "del-effect")


def validate_action_model(generated_domain: Domain, complete_domain: Domain) -> bool:
	"""This function validates whether or not the generated domain is the same as the complete one.

	:param generated_domain: the domain containing the learned action model.
	:param complete_domain: the actual domain that we compare to.
	:return: whether or not the action models are equal.
	"""
	if len(generated_domain.actions) != len(complete_domain.actions):
		print("Action models have different lengths!")
		print(f"Generated - {generated_domain.actions}")
		print(f"Expected - {complete_domain.actions}")
		return False

	for action_name, generated_action_data in generated_domain.actions.items():
		print(f"Checking the action - {action_name}")
		assert action_name in complete_domain.actions
		expected_action = complete_domain.actions[action_name]

		if (validate_preconditions(generated_action_data, expected_action) and
				validate_add_effects(generated_action_data, expected_action) and
				validate_delete_effects(generated_action_data, expected_action)):
			continue

		return False

	return True
