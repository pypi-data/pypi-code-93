"""Module to validate the correctness of the learned action models that were generated."""
import csv
import logging
import os
import signal
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, NoReturn, Dict, List, Any

from heuristics import lm_cut
from pddl.parser import Parser
from pddl.pddl import Domain
from pyperplan import search_plan
from search import greedy_best_first_search
from task import Operator

from sam_learner.core import TrajectoryGenerator
from sam_learner.sam_models import Trajectory

PLAN_SEARCH_TIME_LIMIT = 600
VALID_STATUS = "valid plan!"
INVALID_PLAN_STATUS = "invalid plan!"


class ValidationResult:
	"""Representation of the plan validation result."""
	status: str
	error: Optional[str]

	def __init__(self, status: str, error: Optional[str] = None):
		self.status = status
		self.error = error


class TimeoutException(Exception): pass


@contextmanager
def time_limit(seconds):
	def signal_handler(signum, frame):
		raise TimeoutException("Timed out!")

	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(seconds)
	try:
		yield
	finally:
		signal.alarm(0)


class DomainValidator:
	"""Class that validates the correctness of the domains that were learned by the action model learner.

	The validation process works as follows:
		* Using the learned domain we create plans for the test set problems.
		* For each of the created plans we validate its correctness using the validate URL.
		* We need to validate that the plan that was created is safe, i.e. every action is applicable according to the
			preconditions and effects allowed by the original domain.

	Attributes:
		expected_domain_path: the path to the complete domain containing all of the actions and their preconditions and effects.
	"""

	STATISTICS_COLUMNS_NAMES = ["domain_name", "generated_domain_file_name", "problem_file_name", "plan_generated",
								"plan_validation_status", "validation_error"]

	logger: logging.Logger
	expected_domain_path: str

	def __init__(self, expected_domain_path: str):
		self.logger = logging.getLogger(__name__)
		self.expected_domain_path = expected_domain_path

	def write_plan_file(self, plan_actions: List[Operator], solution_path: Path) -> NoReturn:
		"""Write the plan that was created using the learned domain file.

		:param plan_actions: the actions that were executed in the plan.
		:param solution_path: the path to the file to export the plan to.
		"""
		self.logger.info(f"Writing the plan file - {solution_path}")
		with open(solution_path, "wt") as solution_file:
			solution_file.writelines([f"{operator.name}\n" for operator in plan_actions])

	def generate_test_set_plans(self, tested_domain_file_path: str,
								test_set_directory: str) -> Dict[str, Optional[str]]:
		"""Generate plans for the given domain file and the given test set directory.

		:param tested_domain_file_path: the path to the tested domain in which we want to create actions for.
		:param test_set_directory: the path to the directory containing the test set problems.
		:return: dictionary containing a mapping between the problem paths and their corresponding solutions.
		"""
		successful_plans = {}
		self.logger.info("Solving the test set problems using the learned domain!")
		for problem_file_path in Path(test_set_directory).glob("*.pddl"):
			self.logger.debug(f"Solving problem - {problem_file_path.stem}")
			try:
				with time_limit(PLAN_SEARCH_TIME_LIMIT):
					self.search_plan_with_time_limit(
						problem_file_path, successful_plans, test_set_directory,
						tested_domain_file_path)

			except TimeoutException as e:
				self.logger.info("Solver execution timed out!")
				successful_plans[str(problem_file_path)] = None

		return successful_plans

	def search_plan_with_time_limit(
			self, problem_file_path: Path, successful_plans: Dict[str, Optional[str]],
			test_set_directory: str, tested_domain_file_path: str) -> NoReturn:
		"""Search for a plan for the specific problem with a time limit so that the process won't go on forever.

		:param problem_file_path: the path to the problem file.
		:param successful_plans: the dictionary containing the successful plans.
		:param test_set_directory: the directory containing the problems to solve.
		:param tested_domain_file_path: the domain used to solve the problems.
		"""
		plan_actions = search_plan(tested_domain_file_path, problem_file_path, greedy_best_first_search,
								   lm_cut.LmCutHeuristic)
		if plan_actions is not None and len(plan_actions) > 0:
			self.logger.info(f"Solution Found from problem -{problem_file_path.stem}!")
			solution_path = Path(test_set_directory, f"{problem_file_path.stem}_plan.solution")
			self.write_plan_file(plan_actions, solution_path)
			successful_plans[str(problem_file_path)] = str(solution_path)

		else:
			self.logger.info(f"Could not find a solution for problem - {problem_file_path.stem}")
			successful_plans[str(problem_file_path)] = None

	def validate_plan(self, problem_path: str, plan_path: str) -> ValidationResult:
		"""Validate the correctness of the learned domain against the domain learned using the learner algorithm.

		:param problem_path: the to the test set problem.
		:param plan_path: the path to the plan generated by a solver.
		:return: an object representing the validation status of the plan.
		"""
		self.logger.info(f"Validating the plan generated for the problem - {problem_path}")
		trajectory_generator = TrajectoryGenerator(self.expected_domain_path, problem_path)
		try:
			trajectory_generator.generate_trajectory(plan_path)
			return ValidationResult(VALID_STATUS)

		except AssertionError as error:
			self.logger.warning(f"The plan received is not applicable! {error}")
			return ValidationResult(INVALID_PLAN_STATUS, str(error))

	def extract_applicable_plan_components(self, problem_path: str, plan_path: str) -> Trajectory:
		"""Extract the partial trajectory from the failed plan.

		:param problem_path: the path to the problem file.
		:param plan_path: the path to the failed plan.
		:return: the partial applicable trajectory.
		"""
		self.logger.info(f"Extracting the applicable trajectory from the plan file - {plan_path}")
		trajectory_generator = TrajectoryGenerator(self.expected_domain_path, problem_path)
		return trajectory_generator.generate_trajectory(plan_path, should_return_partial_trajectory=True)

	def write_statistics(self, statistics: List[Dict[str, Any]], output_statistics_path: str) -> NoReturn:
		"""Writes the statistics of the learned model into a CSV file.

		:param statistics: the object containing the statistics about the learning process.
		:param output_statistics_path: the path to the output file.
		"""
		with open(output_statistics_path, 'wt', newline='') as csv_file:
			writer = csv.DictWriter(csv_file, fieldnames=self.STATISTICS_COLUMNS_NAMES)
			writer.writeheader()
			for data in statistics:
				writer.writerow(data)

	@staticmethod
	def clear_plans(created_plans: List[str]) -> NoReturn:
		"""Clears the directory from the plan files so that the next iterations could continue.

		:param created_plans: the paths to the plans that were created in this iteration.
		"""
		for plan_path in created_plans:
			if plan_path is not None:
				os.remove(plan_path)

	def log_model_safety_report(
			self, domain_name: str, generated_domains_directory_path: str, test_set_directory_path: str,
			output_statistics_path: str) -> NoReturn:
		"""The main entry point that runs the validation process for the plans that were generated using the learned
			domains.

		:param domain_name: the name of the domain that is being validated.
		:param generated_domains_directory_path: the path to the directory containing the generated domains.
		:param test_set_directory_path: the directory containing the test set problems.
		:param output_statistics_path: the path to the output statistics file.
		"""
		test_set_statistics = []
		for generated_domain_path in Path(generated_domains_directory_path).glob("*.pddl"):

			domain_successful_plans = self.generate_test_set_plans(
				str(generated_domain_path), test_set_directory_path)
			plan_paths = [plan for plan in domain_successful_plans.values()]
			validated_plans = []
			for problem_path, plan_path in domain_successful_plans.items():
				domain_statistics = {
					"domain_name": domain_name,
					"generated_domain_file_name": generated_domain_path.stem,
					"problem_file_name": Path(problem_path).stem}

				if plan_path is None:
					domain_statistics["plan_generated"] = False
					continue

				validation_status = self.validate_plan(problem_path, plan_path)
				domain_statistics["plan_generated"] = True
				domain_statistics["plan_validation_status"] = validation_status.status
				domain_statistics["validation_error"] = validation_status.error
				validated_plans.append(validation_status.status == VALID_STATUS)
				test_set_statistics.append(domain_statistics)

			self.clear_plans(plan_paths)
			if all(validated_plans):
				self.on_validation_success(output_statistics_path, test_set_statistics)
				return

		self.write_statistics(test_set_statistics, output_statistics_path)
		self.logger.info("Done!")

	def on_validation_success(
			self, output_statistics_path: str,
			test_set_statistics: List[Dict[str, Any]]) -> NoReturn:
		"""Write the needed statistics if the plans were all validated and were approved.

		:param output_statistics_path: the path to the output file.
		:param test_set_statistics: the statistics object containing the data about the learning process.
		"""
		self.logger.info("All plans are valid!")
		self.write_statistics(test_set_statistics, output_statistics_path)
		self.logger.info("Done!")


if __name__ == '__main__':
	try:
		logging.basicConfig(level=logging.DEBUG)
		args = sys.argv
		validator = DomainValidator(args[1])
		validator.log_model_safety_report(
			domain_name=args[2],
			generated_domains_directory_path=args[3],
			test_set_directory_path=args[4],
			output_statistics_path=args[5])

	except Exception as e:
		print(e)
