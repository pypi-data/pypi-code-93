"""Module that contains the trajectory_component class."""
from pddl.pddl import Action
from typing import List

from sam_learner.sam_models.grounded_action import GroundedAction
from sam_learner.sam_models.parameter_binding import ParameterBinding
from sam_learner.sam_models.state import State


class TrajectoryComponent:
	"""Class describing a single step in a trajectory."""

	index: int
	previous_state: State
	grounded_action: GroundedAction
	next_state: State

	def __init__(self, index: int, previous_state: State, action: Action,
				 action_parameters_binding: List[ParameterBinding],
				 next_state: State):
		self.index = index
		self.previous_state = previous_state
		self.grounded_action = GroundedAction(action, action_parameters_binding)
		self.next_state = next_state

	def __str__(self):
		return f"Step number {self.index}: " \
			   f"previous state - {self.previous_state},\n" \
			   f"action applied - {self.grounded_action.activated_action_representation} " \
			   f"the next state - {self.next_state}."
