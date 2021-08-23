"""Yaml Loader Constructors"""
import os

import yaml


def get_yaml_config(filepath: str, loader: yaml.SafeLoader = None) -> dict:
    """flexible yaml loader that takes defaults to safeloader"""
    if loader is None:
        loader = yaml.SafeLoader

    with open(filepath, 'r') as file_:
        return yaml.load(file_, Loader=loader)


class ExtendedSafeLoader(yaml.SafeLoader):
    """Extensible yaml.SafeLoader class where we add extra constructor"""

    # pylint: disable=too-many-ancestors
    def __init__(self, stream):
        """init ExtendedSafeLoader"""
        self._root = os.path.split(stream.name)[0]
        super().__init__(stream)

    def include(self, node):
        """yaml.load macro to add !include function to import other yamls into current"""
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as file_:
            return yaml.load(file_, Loader=ExtendedSafeLoader)

    def join(self, node):
        """yaml.load macro to include string !join function"""
        seq = self.construct_sequence(node)
        return ''.join([str(i) for i in seq])

    def load_sql(self, node):
        """yaml.load macro to include !load_sql function"""
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as file_:
            return file_.read()

    def load_env(self, node):
        """yaml.load macro to include !env function"""
        env_var_name = self.construct_scalar(node)
        return os.environ[env_var_name]

    def fullpath(self, node):
        """yaml.load macro to get fullpath of python __main__ file"""
        return os.path.join(self._root, self.construct_scalar(node))

    def load_many(self, node):
        """yaml.load macro to add !include function to import other yamls into current"""
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as file_:
            config = yaml.load(file_, Loader=ExtendedSafeLoader)

        dag_tasks = {}
        for task in config.get('tasks'):
            name_ = task.get('name')
            object_ = task.get('object')

            if name_ not in dag_tasks:
                dag_tasks[name_] = {
                    **config.get('default'),
                    **object_,
                    **{'task_id': name_}
                }

        return dag_tasks
