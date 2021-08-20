import logging
import json

import multidict

from metaindex import shared


SUFFIX = '.json'


def get(filename, prefix):
    logging.debug(f"Reading JSON metadata from {filename}")
    success, data = _read_json_file(filename)

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
    logging.debug(f"Reading collection JSON metadata from {filename}")
    success, data = _read_json_file(filename)

    if not success:
        return {}

    result = {}
    basepath = filename.parent

    for targetfile in data.keys():
        if not isinstance(data[targetfile], dict):
            logging.warning(f"Key {targetfile} in {filename} is not a dictionary. Skipping.")
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
    """Store this metadata information in that metadata file"""
    raise NotImplementedError()


def _read_json_file(filename):
    try:
        data = json.loads(filename.read_text())
    except json.JSONDecodeError as exc:
        logging.error(f"Failed to read metadata from {filename}: {exc}")
        return False, {}

    if not isinstance(data, dict):
        logging.error(f"JSON metadata file {filename} does not contain a dictionary")
        return False, {}

    return True, data

