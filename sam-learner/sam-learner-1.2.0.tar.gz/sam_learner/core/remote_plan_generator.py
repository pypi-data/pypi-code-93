"""Module to export plans using a remote solver server."""
import logging
import sys
from http import HTTPStatus
from pathlib import Path
from typing import NoReturn

import requests
from requests import Response

SOLVE_URL = 'http://solver.planning.domains/solve'
SOLVE_AND_VALIDATE_URL = 'http://solver.planning.domains/solve-and-validate'


class RemotePlansGenerator:
    """Class that uses an external service to generate plans for the learner algorithm.

    Attributes:
        logger: the logger of the class.
    """

    logger = logging.Logger

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def export_plan_from_response(self, problems_directory_path: str, problem_file_path: Path,
                                  response: Response) -> NoReturn:
        """Export the plan if exists into a solution file.

        :param problems_directory_path: the directory in which we export the output file to.
        :param problem_file_path: the path to the problem file (used to generate the solution
            file's name.
        :param response: the response that was returned from the solving server.
        """
        if response.status_code < HTTPStatus.BAD_REQUEST:
            response_data: dict = response.json()
            if "plan" not in response_data["result"]:
                return

            if response_data["result"]["val_status"] == "err":
                self.logger.debug(response_data["result"]["val_stdout"])
                return

            with open(Path(problems_directory_path, f"{problem_file_path.stem}_plan.solution"),
                      "wt") as plan_file:
                self.logger.debug("Solution Found!")
                plan_file.write(
                    '\n'.join([action["name"] for action in response_data["result"]["plan"]]))

    def generate_plans(self, domain_file_path: str, problems_directory_path: str, validate: bool = False) -> NoReturn:
        """Generates the plans using the solver that exists in the web.

        :param domain_file_path: the path to the domain file.
        :param problems_directory_path: the path to the directory containing the problems needed to solve.
        :param validate: whether or not to validate the input plans.
        """
        for file_path in Path(problems_directory_path).glob("*.pddl"):
            self.logger.info(f"Solving the problem {file_path.stem}")
            with open(domain_file_path, "rt") as domain_file, open(file_path, "rt") as problem_file:
                data = {"domain": domain_file.read(), "problem": problem_file.read()}
                url = SOLVE_AND_VALIDATE_URL if validate else SOLVE_URL
                response: Response = requests.post(url, verify=False, json=data)
                self.export_plan_from_response(problems_directory_path, file_path, response)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    RemotePlansGenerator().generate_plans(domain_file_path=sys.argv[1], problems_directory_path=sys.argv[2])
