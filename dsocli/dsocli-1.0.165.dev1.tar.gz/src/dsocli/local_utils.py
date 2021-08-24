import os
import re
from .contexts import Contexts
from .logger import Logger
from .stages import Stages
from dsocli.config import Configs
from dsocli.file_utils import *


def get_local_path(stage, key=None, prefix=None):
    return prefix + encode_local_path(stage, key)


def encode_local_path(stage, key):
    result = Stages.normalize(stage)
    if key:
        result = os.path.join(result, key)
    return result.replace('/', os.sep)


def decode_local_path(path):
    """
        path is in the form of [/]stage/env_no/[key]
    """
    parts = path.split(os.sep)
    if not parts[0]: parts.pop(0)
    stage = f"{parts[0]}/{parts[1]}"
    if len(parts) > 2:
        key = os.sep.join(parts[2:])
        return stage, key
    else:
        return stage



def get_hierachy_local_paths(stage, key, prefix='', allow_stages=False, uninherited=False, reverse=False):
    stage = Stages.normalize(stage)
    result = []
    if uninherited:
        result.append(get_local_path(stage, key, prefix))
    else:
        ### Add the application context: /project/application/default/0
        result.append(get_local_path('default/0', key, prefix))
        if allow_stages and not Stages.is_default(stage):
            ### Add the project stage context: /project/application/stage/0
            result.append(get_local_path(Stages.get_default_env(stage), key, prefix))
            ### Add the application numbered stage context: /dso/project/application/stage/env
            if not Stages.is_default_env(stage):
                result.append(get_local_path(stage, key, prefix))

    if reverse:
        result = list(reversed(result))

    return result


def load_local_resources(result, path, include_contents=False, filter=None):
    for pth, subdirs, files in os.walk(path):
        for name in files:
            filePath = os.path.join(pth, name)
            if is_binary_file(filePath): continue
            key = filePath[len(path)+1:].replace(os.sep, '/')
            if filter and not re.match(filter, key): continue
            if key in result:
                Logger.warn("Inherited template '{0}' overridden.".format(key))
            result[key] = {
                'Path': filePath,
                'Date': get_file_modified_date(filePath)
            }
            if include_contents:
                with open(filePath, 'r', encoding='utf-8') as f:
                    result[key]['Contents'] = f.read()

    return result



def _patch_resource(resource, prefix):
    if os.path.isabs(resource['Path']):
        resource['Path'] = resource['Path'][len(Configs.working_dir) + 1:]
    ### set Scope if it has not previousely been set, i.e. for newly loaded resources
    if not 'Scope' in resource.keys():
        resource['Scope'] = Contexts.translate_context('project', 'application', decode_local_path(resource['Path'][len(prefix):])[0])
    ### set Stage if it has not previousely been set, i.e. for newly loaded resources
    if not 'Stage' in resource.keys():
        resource['Stage'] = Stages.shorten(decode_local_path(resource['Path'][len(prefix):])[0])
    ### set Origin if it has not previousely been set, i.e. for newly loaded resources
    if not 'Origin' in resource.keys():
        resource['Origin']= {
            'Project': Configs.project,
            'Application': Configs.application,
            'Stage': Stages.shorten(decode_local_path(resource['Path'][len(prefix):])[0]),
        }


def load_context_resources(stage, prefix='', uninherited=False, include_contents=False, filter=None):
    paths = get_hierachy_local_paths(stage, key=None, prefix=prefix, allow_stages=(not stage is None), uninherited=uninherited)
    resources = {}
    for path in paths:
        Logger.debug(f"Loading resource: path={path}")
        load_local_resources(resources, os.path.join(Configs.working_dir, path), include_contents=include_contents, filter=filter)
        for k in resources: _patch_resource(resources[k], prefix)

    return resources


def locate_resource_in_context_hierachy(stage, key, prefix='', uninherited=False):
    resources = {}
    paths = get_hierachy_local_paths(stage, key=None, prefix=prefix, allow_stages=(not stage is None), uninherited=uninherited, reverse=True)
    for path in paths:
        load_local_resources(resources, os.path.join(Configs.working_dir, path), include_contents=True, filter=key)
        for k in resources: _patch_resource(resources[k], prefix)
        if key in resources: break

    return resources
