import os
import yaml


class YamlLoader:
    def __init__(self, default_filename=None):
        self.data = {}
        self.default_filename = default_filename if default_filename else None

    def load(self, filename=None):
        if not filename:
            filename = self.default_filename

        fullpath = os.path.abspath(filename)

        # Short-circuit if already loaded
        if fullpath in self.data:
            return self.data[fullpath]

        # if file doesn't exist
        if not os.path.exists(fullpath):
            raise FileNotFoundError(fullpath)

        with open(fullpath) as fd:
            module = yaml.load(fd, Loader=yaml.SafeLoader)

        self.data[fullpath] = module
        return module

    def has_section(self, section_name, filename=None):
        module = self.load(filename)
        return section_name in module

    def get_section(self, section_name, filename=None):
        if self.has_section(section_name, filename):
            module = self.load(filename)
            return module[section_name]
        else:
            raise SectionNotDefined(filename, section_name)


class SectionNotDefined(Exception):
    def __init__(self, filename, function_name):
        super().__init__(
            f'The function "{function_name}" is not defined in "{filename}".'
        )
