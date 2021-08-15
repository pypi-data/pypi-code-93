import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from yappa.settings import HANDLERS

MIN_MEMORY, MAX_MEMORY = 134217728, 2147483648

SIZE_SUFFIXES = {
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
}


def convert_size_to_bytes(size_str):
    for suffix in SIZE_SUFFIXES:
        if size_str.lower().endswith(suffix):
            size = int(size_str[0:-len(suffix)]) * SIZE_SUFFIXES[suffix]
            if not MIN_MEMORY <= size <= MAX_MEMORY:
                raise ValueError("Sorry. Due to YandexCloud limits, function "
                                 "memory should be between 128mB and 2GB")
            return size
    raise ValueError("Oops. Couldn't parse memory limit. "
                     "It should be in format 128MB, 2GB")


def get_yc_entrypoint(application_type, raw_entrypoint):
    entrypoint = HANDLERS.get(application_type)
    if application_type == "raw":
        entrypoint = raw_entrypoint
    if not entrypoint:
        raise ValueError(
            f"Sorry, supported app types are: "
            f"{','.join(HANDLERS.keys())}. "
            f"Got {application_type}"
        )
    return entrypoint


def save_yaml(config, filename):
    with open(filename, "w+") as f:
        f.write(yaml.dump(config, sort_keys=False))
    return filename
