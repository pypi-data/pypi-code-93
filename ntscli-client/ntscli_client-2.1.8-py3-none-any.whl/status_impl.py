import json
import sys

from ntscli_cloud_lib.automator import HttpLikeStatusResponse
from ntscli_cloud_lib.stateful_session import stateful_session_mgr

# Implementation libs
from ntsjson.functions import nonblock_target_write, set_log_levels_of_libs


def status_impl(**kwargs):
    set_log_levels_of_libs()

    with stateful_session_mgr(**kwargs) as session:
        try:
            resp, raw = session.status(**kwargs)
            resp: HttpLikeStatusResponse
            nonblock_target_write(kwargs.get("save_to"), resp.body.to_json(indent=4))
            if resp is None or resp.status != 200:
                sys.exit(1)
        except ValueError as ve:
            kwargs.get("save_to", (json.dumps(dict(status=404, error=str(ve)))))
