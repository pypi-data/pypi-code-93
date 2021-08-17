"""This module creates plans using random walk steps. This will extend the amount of actions."""
import logging
import random
import sys

from pathlib import Path

import grounding
from pddl.parser import Parser
from pddl.pddl import Domain, Problem
from typing import NoReturn, List

from task import Task

from sam_learner.sam_models.state import State


class RandomWalkPlansGenerator:
    """Class that generates plans for a domain and a problem using random walk algorithm.

    Attributes:
        logger: the logger of the class.
        domain: the PDDL domain data.
        problem: the PDDL problem data.
    """

    logger: logging.Logger
    domain: Domain
    problem: Problem
    problem_path: Path
    output_directory_path: Path

    def __init__(self, domain_path: str, problem_path: str, output_directory_path: str):
        parser = Parser(domain_path, problem_path)
        self.logger = logging.getLogger(__name__)
        self.domain = parser.parse_domain(read_from_file=True)
        self.problem = parser.parse_problem(dom=self.domain, read_from_file=True)
        self.problem_path = Path(problem_path)
        self.output_directory_path = Path(output_directory_path)

    def generate_single_plan(self, task: Task, max_plan_steps: int) -> List[str]:
        """Generate a plan from a randomly selected applicable actions (the random walk).

        :param task: the task that generates the possible transitions from the initial state.
        :param max_plan_steps: the maximal length of the generated plans.
        :return: a list containing the action sequences that were generated.
        """
        if max_plan_steps <= 0:
            raise ValueError("Given illegal value of steps for the plan!")
        self.logger.info(f"Starting to generate a plan for the domain - {self.domain.name} and "
                         f"the problem - {self.problem.name}")
        actions_sequence = []
        current_state = State(self.problem.initial_state, self.domain).ground_facts()
        num_steps = 0
        while num_steps < max_plan_steps:
            possible_transitions = task.get_successor_states(current_state)
            if len(possible_transitions) == 0:
                return actions_sequence

            action, state = random.choice(possible_transitions)
            self.logger.debug(f"generated the applicable action {action}")
            actions_sequence.append(f"{action.name}\n")
            current_state = state
            num_steps += 1

        actions_sequence[-1] = actions_sequence[-1].strip("\n")
        return actions_sequence

    def generate_plans(self, max_plan_steps: int, num_plans: int) -> List[List[str]]:
        """Generate plans with maximal length given as input.

        :param max_plan_steps: the maximal length of the output plans.
        :param num_plans: the number of plans to generate.
        :returns the plans as action sequences.
        """
        grounded_planning_task: Task = grounding.ground(problem=self.problem)
        plans = []
        while len(plans) < num_plans:
            plan = self.generate_single_plan(grounded_planning_task, max_plan_steps)
            if len(plan) == 0:
                continue

            plans.append(plan)

        return plans

    def export_plans(self, generated_plans: List[List[str]], plan_length: int) -> NoReturn:
        """Export the plans to plan file according to the correct format.

        :param generated_plans: the plans that were generated using random walk.
        :param plan_length: the length of the generated plans.
        """
        for index, plan in enumerate(generated_plans, 1):
            with open(f"{str(self.output_directory_path / self.problem_path.stem)}_plan_"
                      f"{index}_max_len_{plan_length}.solution", "wt") as plan_file:
                plan_file.writelines(plan)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    directory_path = sys.argv[1]
    domain_path = sys.argv[2]
    problem_files_glob = sys.argv[3]
    for file_path in Path(directory_path).glob(f"{problem_files_glob}*.pddl"):
        print(f"working on - {file_path}")
        gen = RandomWalkPlansGenerator(domain_path,
                                       file_path,
                                       directory_path)

        plans = gen.generate_plans(max_plan_steps=30, num_plans=5)
        gen.export_plans(generated_plans=plans, plan_length=30)
