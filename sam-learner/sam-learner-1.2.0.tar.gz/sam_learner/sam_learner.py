"""Module that contains the SAM learner code for single agent problems."""
import logging
import pickle
from pathlib import Path
from typing import List, Tuple, Optional, NoReturn

from pddl.pddl import Domain, Action, Effect
from pyperplan import Parser

from sam_learner.core import PredicatesMatcher, TrajectoryGenerator, extract_effects
from sam_learner.sam_models import GroundedAction, State, TrajectoryComponent, Trajectory, Mode


class SAMLearner:
	"""Class that represents the safe action model learner algorithm."""

	logger: logging.Logger
	working_directory_path: Path
	trajectories: List[Trajectory]
	learned_domain: Domain
	matcher: PredicatesMatcher

	def __init__(
			self, working_directory_path: Optional[str] = None, mode: Mode = "production",
			domain: Optional[Domain] = None):
		self.logger = logging.getLogger(__name__)
		if mode == "development":
			self.matcher = PredicatesMatcher(domain=domain)
			self.learned_domain = domain
			return

		self.working_directory_path = Path(working_directory_path)
		domain_path = self.working_directory_path / "domain.pddl"
		self.learned_domain = Parser(domain_path).parse_domain(read_from_file=True)
		self.learned_domain.actions = {}
		self.matcher = PredicatesMatcher(domain_path=str(domain_path))

	def handle_action_effects(self, grounded_action: GroundedAction, previous_state: State,
							  next_state: State) -> Effect:
		"""Finds the effects generated from the previous and the next state on this current step.

		:param grounded_action: the grounded action that was executed according to the trajectory.
		:param previous_state: the state that the action was executed on.
		:param next_state: the state that was created after executing the action on the previous
			state.
		:return: the effect containing the add and del list of predicates.
		"""
		grounded_add_effects, grounded_del_effects = extract_effects(previous_state, next_state)
		action_effect = Effect()
		action_effect.addlist = action_effect.addlist.union(self.matcher.get_possible_literal_matches(
			grounded_action, grounded_add_effects))
		action_effect.dellist = action_effect.dellist.union(self.matcher.get_possible_literal_matches(
			grounded_action, grounded_del_effects))
		return action_effect

	def add_new_action(self, grounded_action: GroundedAction, previous_state: State,
					   next_state: State) -> NoReturn:
		"""Create a new action in the domain.

		:param grounded_action: the grounded action that was executed according to the trajectory.
		:param previous_state: the state that the action was executed on.
		:param next_state: the state that was created after executing the action on the previous
			state.
		"""
		self.logger.info(f"Adding the action {grounded_action.activated_action_representation} "
						 f"to the domain.")
		new_action = Action(name=grounded_action.lifted_action_name,
							signature=grounded_action.lifted_signature,
							precondition=[],
							effect=None)

		# adding the preconditions each predicate is grounded in this stage.
		possible_preconditions = self.matcher.get_possible_literal_matches(grounded_action,
																		   previous_state.facts)
		new_action.precondition = possible_preconditions

		action_effect = self.handle_action_effects(grounded_action, previous_state, next_state)
		new_action.effect = action_effect
		self.learned_domain.actions[new_action.name] = new_action
		self.logger.debug(
			f"Finished adding the action {grounded_action.activated_action_representation}.")

	def update_action(self, grounded_action: GroundedAction, previous_state: State,
					  next_state: State) -> NoReturn:
		"""Create a new action in the domain.

		:param grounded_action: the grounded action that was executed according to the trajectory.
		:param previous_state: the state that the action was executed on.
		:param next_state: the state that was created after executing the action on the previous
			state.
		"""
		self.logger.info(f"Updating the action - {grounded_action.lifted_action_name}")
		action_name = grounded_action.lifted_action_name
		current_action: Action = self.learned_domain.actions[action_name]
		model_preconditions = current_action.precondition.copy()
		possible_preconditions = self.matcher.get_possible_literal_matches(
			grounded_action, previous_state.facts)

		for precondition in model_preconditions:
			if precondition not in possible_preconditions:
				current_action.precondition.remove(precondition)

		action_effect: Effect = self.handle_action_effects(
			grounded_action, previous_state, next_state)
		current_action.effect.addlist = current_action.effect.addlist.union(action_effect.addlist)
		current_action.effect.dellist = current_action.effect.dellist.union(action_effect.dellist)
		self.logger.debug(f"Done updating the action - {grounded_action.lifted_action_name}")

	def handle_single_trajectory_component(self, component: TrajectoryComponent) -> NoReturn:
		"""Handles a single trajectory component as a part of the learning process.

		:param component: the trajectory component that is being handled at the moment.
		"""
		previous_state = component.previous_state
		grounded_action = component.grounded_action
		next_state = component.next_state
		if grounded_action.lifted_action_name not in self.learned_domain.actions:
			self.add_new_action(grounded_action, previous_state, next_state)

		else:
			self.update_action(grounded_action, previous_state, next_state)

	def get_problem_and_solution_files(self) -> List[Tuple[Path, Path]]:
		"""Get the problem and the solution file paths from the working directory.

		:return: the paths to the problems and their respected plans.
		"""
		paths = []
		for solution_file_path in self.working_directory_path.glob("*.solution"):
			# taskXX_plan --> taskXX
			problem_file_name = solution_file_path.stem.split("_")[0]
			problem_path = self.working_directory_path / f"{problem_file_name}.pddl"
			paths.append((problem_path, solution_file_path))

		return paths

	def create_trajectories(self) -> List[Trajectory]:
		"""Create the trajectories that will be used in the main algorithm.

		:return: the list of trajectories that will be used in the SAM algorithm.
		"""
		self.logger.info("Creating the trajectories for the algorithm.")
		trajectories = []
		domain_path = self.working_directory_path / "domain.pddl"
		stored_trajectories_path = self.working_directory_path / "saved_trajectories"
		if stored_trajectories_path.exists():
			self.logger.debug("Loading the trajectories from the file!")
			with open(stored_trajectories_path, "rb") as trajectories_file:
				return pickle.load(trajectories_file)

		for problem_path, plan_path in self.get_problem_and_solution_files():
			generator = TrajectoryGenerator(str(domain_path), str(problem_path))
			trajectories.append(generator.generate_trajectory(str(plan_path)))

		with open(stored_trajectories_path, "wb") as trajectories_file:
			self.logger.debug("Saving the created trajectories in a file for future usage.")
			pickle.dump(trajectories, trajectories_file)

		self.logger.info("Done creating the trajectories! Now you can start running the learning "
						 "algorithm.")
		return trajectories

	def learn_action_model(self, trajectories: List[Trajectory]) -> Domain:
		"""Learn the SAFE action model from the input trajectories.

		:param trajectories: the list of trajectories that are used to learn the safe action model.
		:return: a domain containing the actions that were learned.
		"""
		# First making sure that the domain doesn't have any actions.
		self.logger.info("Starting to learn the action model!")
		for trajectory in trajectories:
			for component in trajectory:
				self.handle_single_trajectory_component(component)

		return self.learned_domain
