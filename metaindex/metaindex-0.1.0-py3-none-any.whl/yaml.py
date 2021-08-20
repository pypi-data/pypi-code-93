import logging

import multidict
import yaml

from metaindex import shared


SUFFIX = '.yaml'


def get(filename, prefix):
    logging.debug(f"Reading YAML metadata from {filename}")

    success, data = _read_yaml_file(filename)

    if not success:
        return {}

    result = multidict.MultiDict()

    for key in data.keys():
        values = data[key]

        if not isinstance(values, list):
            values = [values]

        for value in values:
            result.add(prefix + key, value)

    result.add(shared.IS_RECURSIVE, False)

    return result


def get_for_collection(filename, prefix):
    logging.debug(f"Reading collection YAML metadata from {filename}")
    success, data = _read_yaml_file(filename)

    if not success:
        return {}

    result = {}
    basepath = filename.parent

    for targetfile in data.keys():
        if not isinstance(data[targetfile], dict):
            logging.warnning(f"Key {targetfile} in {filename} is not a dictionary. Skipping.")
            continue

        if targetfile in ['*', '**']:
            fulltargetname = basepath
        else:
            fulltargetname = basepath / targetfile

        if fulltargetname not in result:
            result[fulltargetname] = multidict.MultiDict()

        for key in data[targetfile].keys():
            values = data[targetfile][key]

            if not isinstance(values, list):
                values = [values]

            for value in values:
                result[fulltargetname].add(prefix + key, value)

        result[fulltargetname].add(shared.IS_RECURSIVE, targetfile == '**')

    return result


def store(metadata, filename):
    raise NotImplementedError()


def _read_yaml_file(filename):
    try:
        data = yaml.safe_load(filename.read_text())
    except:
        raise

    if not isinstance(data, dict):
        logging.error(f"YAML metadata file {filename} does not contain a dictionary")
        return False, {}

    return True, data

