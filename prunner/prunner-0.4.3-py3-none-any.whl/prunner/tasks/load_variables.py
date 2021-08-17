from prunner.loaders import YamlLoader
from prunner.util import shellexpand
from prunner.util import split_file_component
from .base import TaskStrategy


class LoadVariablesTask(TaskStrategy):
    def __init__(self, default_filename):
        self.loader = YamlLoader(default_filename)

    @classmethod
    def from_settings(cls, settings):
        return LoadVariablesTask(f"{settings['PRUNNER_CONFIG_DIR']}/variables.yaml")

    @classmethod
    def task_name(cls):
        return "load_variables"

    def execute(self, params, variables=None):
        if type(params) != str:
            raise TypeError(
                "Expecting a string with the set of variables to load. Instead received: ",
                params,
            )

        section_name, filename = split_file_component(params)
        raw_variables = self.loader.get_section(section_name, filename)
        expanded_variables = shellexpand(raw_variables, variables)
        return expanded_variables
