import json
import multiprocessing
import operator
import os
import re
import signal
import subprocess
import sys
import time
from abc import ABC
from contextlib import closing
from functools import reduce  # forward compatibility for Python 3
from shutil import copyfile
from urllib.parse import urlparse

import yaml

from .prompts import Colors
from .prompts import Prompt


class ParseDictByString:
    @staticmethod
    def check_for_split_char(char, value):
        if char in value:
            return value.split(char)
        return value

    @staticmethod
    def get_from_dict(data, map_list):
        keys = []
        for index, key in enumerate(map_list):
            matches = re.search(r'([a-zA-Z0-9\.]*)\[(\d+)\].*', key)
            if not matches:
                keys.append(key)
                continue
            data = ParseDictByString.get_from_dict(data, keys)
            indexes = re.findall(r'\[(\d+)\]', key)
            value = data[key.split('[')[0]]

            # Super hacky - todo - find another way to configure the colon
            value = ParseDictByString.check_for_split_char(':', value)
            for index_ in indexes:
                value = value[int(index_)]
                value = ParseDictByString.check_for_split_char(':', value)

            remaining_keys = map_list[index:]
            if remaining_keys and isinstance(value, dict):
                return ParseDictByString.get_from_dict(value, remaining_keys)
            return value

        return reduce(operator.getitem, map_list, data)

    @staticmethod
    def set_in_dict(data, map_list, value):
        ParseDictByString.get_from_dict(data, map_list[:-1])[map_list[-1]] = value


class BackgroundSubprocess(multiprocessing.Process):
    def __init__(self, cmd, display_stdout=True, on_error_fn=None, env_dict=None):
        self.stdout = None
        self.stderr = None
        self.env_dict = env_dict
        self.cmd = cmd
        self.display_stdout = display_stdout
        self.on_error_fn = on_error_fn
        super().__init__()

    def run(self):
        with subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0,
                              env=self.env_dict) as proc:
            try:
                for line in proc.stdout:
                    formatted = line.rstrip().decode('utf-8', 'ignore')
                    if self.display_stdout:
                        print(formatted)
            except:
                pass
        if proc.returncode != 0:
            if self.on_error_fn:
                self.on_error_fn()


class HelperMixin:
    BACKGROUND_PROCS = []

    def __init__(self):
        self.ROOT_DIR = os.path.abspath(os.path.join(os.getcwd(), '..'))
        signal.signal(signal.SIGINT, self.signal_handler)
        self.kill_captured = False
        self.check_if_docker_is_started()

    def check_if_docker_is_started(self):

        def offline():
            Prompt.error(
                "Docker Engine is offline.  Please start before continuing.")
            sys.exit(1)

        self.execute("docker info", {}, display_stdout=False, show_notice=False, on_error_fn=offline,
                     display_stderr=False)

    @staticmethod
    def create_secret():
        import secrets
        alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join(secrets.choice(alphabet) for i in range(50))

    def check_if_valid_uri(self, x):
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc])
        except:
            return False

    def cleanup(self):
        for proc in self.BACKGROUND_PROCS:
            proc.terminate()

    def execute(self, cmd, env_dict, display_stdout=True, on_error_fn=None, show_env=False,  # noqa: C901
                show_notice=True, exit_on_fail=True, threaded=False, display_stderr=True):
        env = os.environ.copy()
        normalized_dict = {}
        for key, value in env_dict.items():
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            if value is None:
                value = ""
            normalized_dict[key] = value
        env.update(normalized_dict)
        output = ""
        if show_notice:
            Prompt.notice(f"Executing command: {Colors.WARNING}{cmd}")
            if show_env:
                Prompt.notice(
                    f"Environment Variables: {json.dumps(env_dict, indent=4, sort_keys=True)}")
        if threaded:
            proc = BackgroundSubprocess(
                cmd, display_stdout=display_stdout, on_error_fn=on_error_fn, env_dict=env)
            proc.daemon = True
            proc.start()
            self.BACKGROUND_PROCS.append(proc)
        else:
            args = dict(bufsize=0, env=env, shell=True)
            if not display_stderr:
                args.update(dict(stderr=subprocess.DEVNULL))
            if not display_stdout:
                args.update(dict(stdout=subprocess.PIPE))
            with subprocess.Popen(cmd, **args) as proc:
                if args.get('stdout') == subprocess.PIPE:
                    for line in proc.stdout:
                        formatted = line.rstrip().decode('utf-8', 'ignore')
                        output += formatted
            if proc.returncode != 0:
                if on_error_fn:
                    on_error_fn()
                Prompt.error(
                    f"[{cmd}] Failed [code:{proc.returncode}]- {proc.stderr}", close=exit_on_fail)
            return output

    def signal_handler(self, sig, frame):
        Prompt.notice("\nCtrl-c captured.  Executing teardown function.")
        if not self.kill_captured:
            self.kill_captured = True
            self.on_sig_kill()
        sys.exit(0)

    def on_sig_kill(self):
        raise NotImplementedError()

    def on_complete(self):
        raise NotImplementedError()

    def on_fail(self):
        raise NotImplementedError()

    def check_if_container_is_ready(self, name):
        return self.execute(cmd="docker inspect --format=\"{{json .State.Health.Status}}\" " + name,
                            env_dict={}, exit_on_fail=True,
                            display_stdout=False, show_notice=False)


class Runner(HelperMixin, ABC):
    REQUIRED_PORTS = []  # Verifies to see if ports are available

    def execute(self, cmd, env_dict=None, display_stdout=True, on_error_fn=None, show_env=False, show_notice=True,
                exit_on_fail=True, threaded=False, display_stderr=True):
        if not env_dict:
            env_dict = {}
        return super().execute(cmd,
                               display_stdout=display_stdout,
                               env_dict=env_dict,
                               show_notice=show_notice,
                               threaded=threaded,
                               exit_on_fail=exit_on_fail,
                               display_stderr=display_stderr,
                               on_error_fn=on_error_fn if on_error_fn else self.on_fail, show_env=show_env)

    def check_ports(self, raise_exception=True):
        Prompt.notice(
            f"Checking if ports are available for deployment: {self.REQUIRED_PORTS}")
        import socket
        ports_in_use = []
        for port in self.REQUIRED_PORTS:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                if sock.connect_ex(('127.0.0.1', port)) == 0:
                    ports_in_use.append(port)
        if ports_in_use and raise_exception:
            Prompt.error(
                f"Cannot deploy.  The following ports are in use: {ports_in_use}", close=True)
        return bool(ports_in_use)

    def run(self):
        raise NotImplementedError()


class DockerComposeRunner(Runner):
    COMPOSE_PROJECT_NAME = None
    REQUIRED_PORTS = []  # Add or override
    COMPOSE_FILES = ["docker-compose.yml"]  # Add or override
    SERVICES = []  # Add or override
    STACK = None
    BASE_DIR = None

    def __init__(self):
        assert self.COMPOSE_PROJECT_NAME, "Make sure that you've set `COMPOSE_PROJECT_NAME`"
        assert self.STACK, "Make sure that you've set `STACK`"
        assert self.BASE_DIR, "Make sure that you've set `BASE_DIR`"
        self.config = {}
        self.env = dict(COMPOSE_PROJECT_NAME=self.COMPOSE_PROJECT_NAME)
        docker_compose_configs = self.load_docker_compose_files()
        flattened_configs = {}
        for config in docker_compose_configs:
            flattened_configs.update(config['services'])
            for service, configuration in config['services'].items():
                self.SERVICES.append(dict(name=service, **configuration))
        for service in self.SERVICES:
            service['stack_config'] = self.get_service_config(service['name'], flattened_configs)
            # This only allows a single namespace so env vars must be different across services
            self.env.update(self.get_service_environment_variables(service['name'], flattened_configs))
        super().__init__()
        self.REQUIRED_PORTS = sorted([int(item.split(':')[0])
                                      for sublist in [x.get('ports', []) for x in self.SERVICES] for item in sublist])

    def wait_for_health_checks(self):
        Prompt.warning("Waiting for stack to come up...")

        for service in [x for x in self.SERVICES if x.get('healthcheck')]:
            while True:
                status = self.check_if_container_is_ready(
                    self.generate_compose_name(service['name']))
                if status == '"healthy"':
                    break
                time.sleep(1)

    def get_config_node(self, node, config=None):
        if not config:
            config = self.config
        return config[node]

    def get_service_node(self, node):
        return next((item for item in self.SERVICES if item["name"] == node))

    def generate_compose_name(self, node, instance_number=1):
        return f"{self.COMPOSE_PROJECT_NAME}_{node}_{instance_number}"

    def load_yaml(self, path):
        with open(path, 'r') as stream:
            return yaml.safe_load(stream)

    def load_docker_compose_files(self):
        data = []
        for compose_file in self.COMPOSE_FILES:
            config = self.load_yaml(os.path.join(self.BASE_DIR, compose_file))
            for name, service in config['services'].items():
                service['fullname'] = self.generate_compose_name(name)
            data.append(config)
        return data

    def parse_and_interpolate_yml(self, path, docker_compose_configs):
        if os.path.exists(path):
            config = self.load_yaml(path)
            if not config:
                return {}
            for key, value in config.items():
                matches = re.findall(r'\${.*?}', value)
                for match in matches:
                    keys = match.replace('${', '').replace('}', '').split('.')
                    new_value = ParseDictByString.get_from_dict(docker_compose_configs, keys)
                    config[key] = config[key].replace(match, new_value)
            return config
        return {}

    def get_service_config(self, service, docker_compose_configs):
        path = os.path.join(self.BASE_DIR, 'services', service, 'config', self.STACK, 'config.yml')
        return self.parse_and_interpolate_yml(path, docker_compose_configs)

    def get_service_environment_variables(self, service, docker_compose_configs):
        path = os.path.join(self.BASE_DIR, 'services', service, 'config', self.STACK, 'environment_vars.yml')
        return self.parse_and_interpolate_yml(path, docker_compose_configs)

    def generate_config(self):
        config = {x['name']: x['stack_config'] for x in self.SERVICES}
        with open("environment.json", 'w') as f:
            json.dump(config, f, indent=4, sort_keys=True)
        self.config = config
        copyfile("environment.json", os.path.join(self.BASE_DIR, 'environment.json'))

    def load_config(self, reuse_existing=True):
        if not reuse_existing or not os.path.exists("environment.json"):
            self.generate_config()
        else:
            with open("environment.json", 'r') as f:
                config = json.load(f)
            self.config = config

    def generate_docker_file_command(self):
        return " ".join([f"-f {x}" for x in self.COMPOSE_FILES])

    def run(self, **kwargs):
        raise NotImplementedError()

    def on_sig_kill(self):
        raise NotImplementedError()

    def on_complete(self):
        raise NotImplementedError()

    def on_fail(self):
        raise NotImplementedError()
