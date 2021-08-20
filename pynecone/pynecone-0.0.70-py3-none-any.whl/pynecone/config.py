import yaml
import os
import sys

import importlib
import pkgutil


def get_config_name():
    main = sys.modules['__main__']
    if hasattr(main, '__file__'):
        return os.path.splitext(main.__file__)[0]
    else:
        return __name__


class Config:

    def __init__(self, name='{0}.yml'.format(get_config_name()), path=os.getcwd()):
        self.path = path
        self.full_path = os.path.join(path, name)
        self.data = {}

    def load(self):
        with open(self.full_path) as file:
            self.data = yaml.safe_load(file)

    def save(self):
        with open(self.full_path, 'w') as file:
            yaml.dump(self.data, file)

    def get_blank_environment(self, name):
        return {
            'name': name
        }

    def create_environment(self, name):
        self.generate()

        found = [env for env in self.data.get('environments') if env['name'] == name]

        if found:
            return None

        env = self.get_blank_environment(name)
        self.data['environments'].append(env)
        self.save()
        return env

    def delete_environment(self, name):
        self.generate()

        found = [env for env in self.data.get('environments') if env['name'] == name]

        if found:
            if found[0]['name'] == self.data['active_environment']:
                print('cannot delete the active environment {0}'.format(name))
                return None
            else:
                self.data['environments'] = [i for i in self.data['environments'] if i['name'] != name]
                self.save()
                return name
        else:
            return None

    def set_active_environment(self, name):
        self.generate()

        found = [env for env in self.data.get('environments') if env['name'] == name]
        if found:
            self.data['active_environment'] = name
            self.save()
            return found
        else:
            return None

    def get_active_environment(self):
        self.generate()

        found = [env for env in self.data.get('environments') if env['name'] == self.data['active_environment']]
        if found:
            return found[0]
        else:
            return None

    def get_active_environment_name(self):
        self.generate()

        return self.data['active_environment']

    def list_environments(self):
        self.generate()

        return self.data['environments']

    def get_environment(self, name, yaml=False):
        self.generate()

        found = [env for env in self.data.get('environments') if env['name'] == name]
        if found:
            if yaml:
                return yaml.dump(found[0])
            else:
                return found[0]
        else:
            return None

    def create_entry(self, section, name, **kwargs):
        env = self.get_active_environment()

        entries = env.get(section)

        if not entries:
            entries = []
            env[section] = entries

        if [entry for entry in entries if entry['name'] == name]:
            return None

        entry = dict(kwargs)
        entry['name'] = name
        entries.append(entry)
        self.save()
        return entry

    def get_entry_cfg(self, section, name, outputYaml=False):
        entry = [entry for entry in self.list_entries(section) if entry['name'] == name]
        if entry:
            return yaml.dump(entry[0]) if outputYaml else entry[0]
        else:
            return None

    def put_entry_cfg(self, section, name, outputYaml=False, **kwargs):
        entries = [entry for entry in self.list_entries(section) if entry['name'] != name]
        entry = dict(kwargs)
        entry['name'] = name
        entries.append(entry)
        self.save()
        return yaml.dump(entry) if outputYaml else entry

    def put_entry_value(self, section, name, key, value):
        entry = [entry for entry in self.list_entries(section) if entry['name'] == name]
        if entry:
            entry[0][key] = value
        else:
            entry = {'name': name, key: value}
            self.append_entry(section, entry)
        self.save()

    def get_entry_value(self, section, name, key, default=None):
        entry = [entry for entry in self.list_entries(section) if entry['name'] == name]
        if entry:
            return entry[0].get(key, default)
        else:
            return default

    def get_entry_instance(self, section, name):
        cfg = self.get_entry_cfg(section, name)
        if cfg:
            for pkg in [pkg_name for _, pkg_name, _ in pkgutil.iter_modules() if pkg_name.endswith('_modules')]:
                for _, mod, _ in pkgutil.iter_modules([importlib.import_module(pkg).__path__[0]]):
                    if mod.startswith('{0}_'.format(section)):
                        if mod.endswith('_{0}'.format(cfg['type'])):
                            print('*** loading module {0}.{1}'.format(pkg, mod))
                            mod_cfg = dict(cfg)
                            mod_cfg['name'] = name
                            return getattr(importlib.import_module('{0}.{1}'.format(pkg, mod)),
                                           'Module')().get_instance(**mod_cfg)
        return None

    def list_entries(self, section):
        env = self.get_active_environment()
        entries = env.get(section)
        return entries if entries else []

    def append_entry(self, section, entry):
        env = self.get_active_environment()
        entries = env.get(section)
        if entries:
            entries.append(entry)
        else:
            env[section] = [entry]

    def delete_entry(self, section, name):
        env = self.get_active_environment()
        found = [entry for entry in env[section] if entry['name'] == name]

        if found:
            env[section] = [i for i in env[section] if i['name'] != name]
            self.save()
            return name
        else:
            return None

    def list_commands(self):
        return []
        self.get_active_environment()
        entry_mods = [m.split('_')[1] for m in self.modules if m.startswith('modules.{0}_'.format('module'))]
        return [getattr(importlib.import_module('modules.{0}_{1}'.format('module', entry_mod)), 'Module')().get_instance() for entry_mod in entry_mods]


    def get_timeout(self):
        return 20

    def get_active_environment_name(self):
        self.generate()

        return self.data['active_environment']

    def generate(self, force=False):
        if self.data.get('environments') is None or force:
            print('*** generating default config file ***')

            self.data = {
                'environments': [
                        self.get_blank_environment('local')
                ],
                'active_environment': 'local'}

            self.save()


    @classmethod
    def init(cls, name='config.yml', path=os.getcwd()):
        cfg = Config(name, path)

        if not os.path.exists(cfg.full_path):
            cfg.generate()

        cfg.load()
        return cfg
