import logging
import os


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def interpret_label(label: str):
    out = {}
    if label.startswith('@'):
        label = label.lstrip('@')
        parts = label.splitlines('/', 2)
        if len(parts) == 1:
            return {'repository': label, 'package': '', 'target': label}
        out['repository'] = parts[0]
        label = f'/{parts[1]}'
    parts = label.split(':', 2)
    parts[0] = remove_prefix(parts[0], "//")
    logging.info(parts)
    out['package'] = parts[0]
    if len(parts) == 2 and parts[1] != "":
        out['target'] = parts[1]
    elif not label.startswith("//"):
        out['target'] = label
        out['package'] = ''
    else:
        out['target'] = os.path.basename(parts[0])
    return out


BUILD_FILE_NAMES = ['BUILD.bazel', 'BUILD', 'BUCK']


def interpret_label_for_workspace_location(target:str, workspace_location:str):
    label = interpret_label(target)
    repo = label.get('repository', None)
    pkg = label.get('package', None)
    rule = label.get('target', None)
    if repo:
        logging.error(f"repository detection not implemented {target}")
        exit(1)

    if target.startswith("//"):
        for build_file_name in BUILD_FILE_NAMES:
            build_file = os.path.join(workspace_location, pkg, build_file_name)
            if os.path.isfile(build_file):
                return build_file, pkg, rule

    logging.error(f"could not find label from workspace location {target} {workspace_location}")
    exit(1)
