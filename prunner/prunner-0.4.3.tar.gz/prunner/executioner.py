import copy
from pprint import PrettyPrinter

from prunner import loaders
from prunner.tasks import STANDARD_TASKS


class Executioner:
    def __init__(self, variables, tasks=STANDARD_TASKS):
        for k, v in variables.items():
            variables[k] = typecast(v)
        self.variables = variables
        config_dir = variables["PRUNNER_CONFIG_DIR"]
        yaml_file = f"{config_dir}/pipelines.yaml"
        self.pipeline_loader = loaders.YamlLoader(yaml_file)

        self.tasks = {}
        self.add_tasks(tasks)
        self.printer = PrettyPrinter()

    def add_tasks(self, tasks):
        for task in tasks:
            task_instance = task.from_settings(self.variables)
            self.tasks[task.task_name()] = task_instance

    def execute_pipeline(self, pipeline_name):
        self.variables["PIPELINE_NAME"] = pipeline_name
        pipeline = self.pipeline_loader.get_section(pipeline_name)

        for i, raw_task_dict in enumerate(pipeline):
            raw_task_dict = copy.deepcopy(raw_task_dict)
            task_name, task_params = raw_task_dict.popitem()

            task = self.get_task(task_name)
            task_params = task.modify_params(task_params, self.variables)
            self.print_new_task(i, task_name, task_params)

            updates = self.run_task(task, task_params)
            self.handle_verbose_flag(updates)
            self.variables.update(updates)

    def get_task(self, task_name):
        if task_name not in self.tasks:
            raise ValueError("That task is not available: ", task_name)
        task = self.tasks[task_name]
        return task

    def handle_verbose_flag(self, updates):
        if self.variables["VERBOSE"]:
            new_variables = {
                k: v for k, v in updates.items() if k not in self.variables
            }
            if new_variables:
                print("Results:")
                self.printer.pprint(new_variables)

    def run_task(self, task, params):
        updates = task.execute(params, self.variables)
        if updates is None or type(updates) != dict:
            updates = {}

        for k, v in updates.items():
            updates[k] = typecast(v)

        return updates

    def print_new_task(self, i, task_name, task_value):
        print("-" * 80)
        print(f"Task {i}: {task_name} = {task_value}")


def typecast(value):
    if type(value) != str:
        return value

    v = value.strip().lower()
    if v == "true" or v == "yes":
        return True
    elif v == "false" or v == "no":
        return False
    elif v.isdecimal():
        return int(v)
    else:
        return value
