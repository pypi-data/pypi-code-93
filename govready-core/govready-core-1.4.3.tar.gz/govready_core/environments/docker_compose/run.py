import argparse
from dataclasses import dataclass

try:
    from govready_core.environments.docker_compose.prompts import Prompt
except ImportError:
    from pip._internal import main as pip

    pip(['install', 'govready-core', '--user'])
    from govready_core.environments.docker_compose.prompts import Prompt


@dataclass
class Compose:
    def __init__(self, compose_class, actions):
        self.compose_class = compose_class
        self.actions = actions


class RunEnvironment:
    COMPOSE_MAP = {}
    DESCRIPTION = ""

    def __init__(self):
        base_parser = self.get_parser()
        base_parser.add_argument(
            '--clean', help='Will wipe the database and other artifacts for a clean run', action='store_true')
        self.args = vars(base_parser.parse_known_args()[0])

    def check_action(self, action, valid_actions):
        if action not in valid_actions:
            Prompt.error(f"{action} is not a valid choice.  Choices: {valid_actions}.", close=True)

    def get_compose_runner(self):
        runner = self.args['environment']
        runner_obj = self.COMPOSE_MAP[runner]
        self.check_action(self.args['action'], runner_obj['actions'])
        return runner_obj['runner'](), runner_obj['actions'][self.args['action']]

    def get_parser(self):
        parser = argparse.ArgumentParser(description=self.DESCRIPTION)
        parser.add_argument('action', help='The action to take.')
        parser.add_argument('environment', help='The environment to use.')
        return parser

    def execute(self):
        runner, action = self.get_compose_runner()
        action(runner, self.args)


class RunnerActions:

    @staticmethod
    def run(runner, args):
        runner.run(clean=args['clean'])
        runner.on_complete()
        runner.cleanup()

    @staticmethod
    def wipe_db(runner, args):
        runner.wipe_db()

    @staticmethod
    def init(runner, args):
        runner.generate_config()

    @staticmethod
    def remove(runner, args):
        runner.remove()
