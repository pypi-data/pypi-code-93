from hashlib import md5
from json import dump as json_dump
from logging import getLogger, INFO, DEBUG, basicConfig
from sys import stdout
from typing import List, TypedDict, Sequence

from click import command, argument, option
from staliro import staliro

from .blackbox import ardupilot_blackbox_factory
from .module import load_module
from .storage import store_result

logger = getLogger("ardutest")


@command()
@option("-v", "--verbose", is_flag=True)
@option("-o", "--outfile", default="results.json")
@argument("module_name")
def ardutest(verbose: bool, outfile: str, module_name: str) -> None:
    basicConfig(stream=stdout, level=DEBUG if verbose else INFO)
    getLogger("urllib3").level = INFO
    getLogger("docker").level = INFO

    module = load_module(module_name)
    blackbox = ardupilot_blackbox_factory(module.config, module.stack_config, module.mission_factory)

    logger.debug("Configuring destination directories")

    log_dest = module.config.log_dest
    if log_dest is not None and not log_dest.is_dir():
        log_dest.mkdir()

    mission_dest = module.config.mission_dest
    if mission_dest is not None and not mission_dest.is_dir():
        mission_dest.mkdir()

    result = staliro(blackbox, module.specification, module.optimizer, module.options)
    
    include_hash = module.config.mission_dest is not None or module.config.log_dest is not None

    store_result(result, outfile, include_hash)

if __name__ == "__main__":
    ardutest()
