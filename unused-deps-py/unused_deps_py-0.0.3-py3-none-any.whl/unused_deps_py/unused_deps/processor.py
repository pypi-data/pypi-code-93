import logging
import os
import java_manifest

from typing import List, Dict
from xml.etree import ElementTree

from . import command, aspect
from . workspace import interpret_label_for_workspace_location
from . import strip_prefix_path, get_real_path
from deps_proto import deps_pb2


BAZEL_FLAGS = ["--tool_tag=unused_deps", "--keep_going", "--color=yes", "--curses=yes"]
DIRECT_DEPENDENCIES = "--direct_dependencies"


def invert_dict(src: dict) -> dict:
    return {v: k for k, v in src.items()}


class Processor:
    workspace_path: str = None
    build_tool: str = None
    extra_action_file: str = None
    output_file: str = None
    extra_build_flags: List[str] = None
    targets: List[str] = None
    bazel_bin: str = None
    bazel_output_path: str = None
    bazel_output_base: str = None
    maven_repos: List[str] = None
    maven_jars: Dict[str, str] = None
    jars_to_maven: Dict[str, str] = None

    def __init__(self, workspace_path=None, build_tool=None, extra_action_file=None, output_file=None,
                 extra_build_flags=None, targets=None):
        if extra_action_file:
            logging.error("--extra-action-file is not implemented yet")

        self.workspace_path = workspace_path
        self.build_tool = build_tool
        self.extra_action_file = extra_action_file
        self.output_file = output_file
        self.extra_build_flags = extra_build_flags or list()
        self.targets = targets or ["//..."]
        self.bazel_bin = self.bazel_info('bazel-bin')
        self.bazel_output_path = self.bazel_info('output_path')
        self.bazel_output_base = self.bazel_info('output_base')
        logging.info(f'bazel-bin -> {self.bazel_bin}')
        logging.info(f'bazel output_path -> {self.bazel_output_path}')
        self.maven_repos = self.get_maven_repos()
        self.maven_jars = self.get_maven_jars()
        self.jars_to_maven = invert_dict(self.maven_jars)

    def process(self) -> int:
        targets = " + ".join(self.targets)
        kind = f"\"kind('(kt|java|android)_*', {targets})\""  # we need this one quoted
        targets = self.targets = self.execute_bazel_command('query', kind).splitlines()
        logging.info(f'actual targets: {targets}')

        if len(targets) == 0:
            logging.error("Found no targets of kind (kt|java|android)_*")
            return 1

        with aspect.setup() as aspect_path:
            self.build_with_tool(aspect_path)

        any_printed = False
        for target in targets:
            any_printed = self.process_label(target) or any_printed

        if any_printed is False:
            print("No unused deps found.")

        return 0

    def execute_bazel_command(self, cmd, *args) -> str:
        cmd = [self.build_tool, cmd] + BAZEL_FLAGS + list(args)
        cmd = ' '.join(cmd)
        logging.info(f'going to execute {cmd}')
        return command.output(cmd, cwd=self.workspace_path)

    def build_with_tool(self, aspect_path):
        args = [
            '--output_groups=+unused_deps_outputs',
            f'--override_repository=unused_deps={aspect_path}',
            '--aspects=@unused_deps//:javac_params.bzl%javac_params'
        ] + list(self.extra_build_flags) + self.targets
        self.execute_bazel_command('build', *args)

    def bazel_info(self, key: str) -> str:
        return self.execute_bazel_command('info', key).strip()

    def process_label(self, target: str) -> bool:
        logging.info(f"processing {target}")
        build_file, pkg, rule = interpret_label_for_workspace_location(target, workspace_location=self.workspace_path)
        logging.info(f"parsed label {build_file} {pkg} {rule}")
        deps_by_jar = self.direct_dep_params(self.input_file_name(pkg, rule, 'javac_params'))
        logging.info(f'resolved {len(deps_by_jar.keys())} dependencies passed to {target}')
        if len(deps_by_jar.keys()) == 0:
            return False
        used_deps = list(self.get_used_deps(pkg, rule))
        logging.info(f'resolved {len(used_deps)} actually used dependencies by {target}')
        jars_by_deps = invert_dict(deps_by_jar)
        for used_dep in used_deps:
            if used_dep in jars_by_deps:
                jars_by_deps.pop(used_dep)
        logging.info(f'resolved {len(jars_by_deps.keys())} dependencies that can be removed from {target}')
        unused_deps = invert_dict(jars_by_deps)
        unused_deps.pop(None, None)
        labels = sorted(unused_deps.keys())
        for label in labels:
            print(f"buildozer 'remove deps {label}' {target}")
        return len(labels) > 0


    def input_file_name(self, pkg, rule, extension):
        candidate = os.path.join(self.bazel_bin, pkg, f'lib{rule}.{extension}')
        if os.path.exists(candidate):
            return candidate
        return os.path.join(self.bazel_bin, pkg, f'{rule}.{extension}')

    def direct_dep_params(self, *params_file_names: List[str]) -> Dict[str, str]:
        out = {}
        for params_file_name in params_file_names:
            try:
                for bazel_label, jar_file in self.process_direct_dep_param(params_file_name).items():
                    out[bazel_label] = jar_file
            except Exception as e:
                logging.error(f'failed to process {params_file_name}', e)
        return out

    def process_direct_dep_param(self, params_file_name: str) -> Dict[str, str]:
        if not os.path.exists(params_file_name):
            logging.error(f"couldn't find file {params_file_name}")
            return {}

        f = open(params_file_name, 'r')
        body = f.read()
        if DIRECT_DEPENDENCIES not in body:
            logging.debug(f"{params_file_name} has no {DIRECT_DEPENDENCIES} section")
            return {}

        position = body.index(DIRECT_DEPENDENCIES)
        first = position + len(DIRECT_DEPENDENCIES) + 1
        pending = body[first:]
        out = {}
        for line in pending.splitlines():
            if '--' in line:
                break
            generated_jar_path = get_real_path(os.path.join(self.bazel_output_path,strip_prefix_path(line, 'bazel-out')),'/bazel-out')
            label = self.get_target_from_path(generated_jar_path, line)
            out[label] = line
        return out

    def remove_header_from_jar(self, filename: str) -> str:
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)
        return os.path.join(dirname, basename.replace('header_', ''))

    def get_target_from_path(self, filename: str, original_name:str) -> str:
        manifest = java_manifest.from_jar(filename)[0]
        label = manifest.get('Target-Label', None)
        if label:
            # this is a bazel generated rule
            if label.startswith('@@'):
                label = label[1:]
            logging.debug(f"found possible used library {label} {filename}")
            return label
        if filename in self.jars_to_maven:
            return self.jars_to_maven[filename]
        if original_name in self.jars_to_maven:
            return self.jars_to_maven[original_name]
        candidate = 'external' + original_name.split('external', 1)[1]
        if candidate in self.jars_to_maven:
            return self.jars_to_maven[candidate]
        if os.path.basename(filename).startswith('header_'):
            return self.get_target_from_path(self.remove_header_from_jar(filename),
                self.remove_header_from_jar(original_name))
        logging.error(f"Couldn't resolve {filename} {original_name}")

    def get_maven_repos(self) -> List[str]:
        fetch = "coursier_fetch"
        repos = self.execute_bazel_command('query', '--output=xml', f'"kind({fetch}, //external:all)"')
        parsed = ElementTree.fromstring(repos)
        out = list()
        for rule in parsed.iter('rule'):
            klass = rule.get('class', None)
            if not klass or klass not in [fetch, f'pinned_{fetch}']:
                continue
            name = rule.get('name', None)
            if not name or 'unpinned_' in name:
                logging.info(f'ignoring {name}')
                continue
            out.append(name.replace('//external:', ''))
        return out

    def get_maven_artifacts_from_repository(self, repository) -> List[str]:
        query = self.execute_bazel_command('query', '--output=xml', f'"kind(jvm_import, @{repository}//:all)"')
        query = ElementTree.fromstring(query)
        out = {}
        for rule in query.iter('rule'):
            bazel_rule = rule.attrib.get('name', 'invalid')
            for child in rule.iter('list'):
                name = child.attrib.get('name', 'invalid')
                if name != 'jars':
                    continue
                jars = list(child.iter('label'))
                if len(jars) > 1:
                    logging.error(f"for label {bazel_rule} there's more than 1 jar")
                elif len(jars) == 0:
                    logging.error(f"for label {bazel_rule} there are no jars")
                    continue
                out[bazel_rule] = jars[0].attrib.get('value', 'invalid').replace('@', 'external/').replace('//:', '/')
        logging.info('done parsing repo')
        return out

    def get_maven_jars(self) -> Dict[str, str]:
        out = {}
        for repo in self.maven_repos:
            for rule, jar in self.get_maven_artifacts_from_repository(repo).items():
                out[rule] = jar
        logging.info(f"resolved {len(out.keys())} maven provided jars")
        return out

    def get_used_deps(self, pkg: str, rule: str) -> List[str]:
        jdeps = self.input_file_name(pkg, rule, 'jdeps')
        if not os.path.exists(jdeps):
            return
        body = open(jdeps, 'rb').read()
        dependencies = deps_pb2.Dependencies()
        dependencies.ParseFromString(body)
        for dependency in dependencies.dependency:
            yield dependency.path
