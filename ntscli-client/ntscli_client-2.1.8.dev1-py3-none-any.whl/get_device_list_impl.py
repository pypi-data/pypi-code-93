import json
import sys

from ntscli_cloud_lib.stateful_session import stateful_session_mgr

# Implementation libs
from ntsjson.functions import nonblock_target_write, set_log_levels_of_libs
from ntsjson.log import logger


def get_device_list_impl(rae, configuration, save_to):
    """
    List devices on a remote RAE.
    """
    set_log_levels_of_libs()

    def id_as_json(source_id):
        return source_id.to_dict()

    with stateful_session_mgr(configuration=configuration, rae=rae) as session:
        identifiers = session.get_device_list()
        if identifiers is None:
            logger.critical(
                "We were unable to get the list of device identifiers. This could be a connectivity issue, or the modules may not be "
                "installed on the RAE."
            )
            nonblock_target_write(save_to, "[]")
            sys.exit(1)
        nonblock_target_write(save_to, json.dumps([js for js in map(id_as_json, identifiers)], indent=4))
