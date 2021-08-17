"""Module that represents a state."""
from typing import Tuple, List

from pddl.pddl import Domain, Problem

from sam_learner.sam_models.comparable_predicate import ComparablePredicate
from sam_learner.sam_models.parameter_binding import ParameterBinding


class StateLiteral:
	"""Represent the connection between a lifted and a grounded predicate."""

	fact: str
	domain: Domain

	def __init__(self, fact: str, domain: Domain):
		self.fact = fact
		self.domain = domain

	@classmethod
	def generate_problem_literal(cls, fact: str, domain: Domain, problem: Problem) -> Tuple[
		ComparablePredicate, List[ParameterBinding]]:
		"""Lift the grounded fact.

		:param fact: the fact to lift.
		:param domain: the domain containing all the data about the world.
		:param problem: the problem object containing the information about the concrete objects.
		:return: the mapping between the grounded fact and the lifted predicate.
		"""
		fact_data = fact.strip("()").split(" ")
		predicate_name = fact_data[0]
		predicate_objects = fact_data[1:]
		domain_predicate: ComparablePredicate = domain.predicates[predicate_name]
		bindings = []
		for (parameter_name, _), object_name in zip(domain_predicate.signature, predicate_objects):
			bindings.append(ParameterBinding(parameter_name,
											 (problem.objects[object_name],),
											 object_name))

		return domain_predicate, bindings

	@staticmethod
	def ground(grounding_data: Tuple[ComparablePredicate, List[ParameterBinding]]) -> str:
		"""ground lifted predicate data back to its fact form.

		:param grounding_data: the data of the object to ground.
		:return: the fact as a string form.
		"""
		predicate, bindings = grounding_data
		return f"({predicate.name} [{str(binding for binding in bindings)}])"


class State:
	"""Represent a state containing lifted predicates and their binding."""

	facts: List[ComparablePredicate]
	domain: Domain

	def __init__(self, facts: List[ComparablePredicate], domain: Domain):
		self.domain = domain
		self.facts = facts

	@classmethod
	def generate_problem_state(cls, facts: frozenset, domain: Domain, problem: Problem) -> List[
		Tuple[ComparablePredicate, List[ParameterBinding]]]:
		"""Lift the grounded facts to and returns the lifted facts and their object binding."""
		return [StateLiteral.generate_problem_literal(fact, domain, problem) for fact in facts]

	def __str__(self):
		return str(self.facts)

	def __eq__(self, other):
		return self.facts == other.facts

	def ground_facts(self) -> frozenset:
		"""Ground the facts to a form that the planner can use.

		:returns the grounded facts as a frozen set.
		"""
		grounded_facts = set()
		for fact in self.facts:
			if len(fact.signature) == 0:
				grounded_facts.add(f"({fact.name})")

			else:
				grounded_facts.add(f"({fact.name} {' '.join(item[0] for item in fact.signature)})")

		return grounded_facts
