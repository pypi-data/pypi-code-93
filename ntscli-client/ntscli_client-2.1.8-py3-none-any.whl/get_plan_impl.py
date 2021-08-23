from io import BytesIO
from typing import Optional

from ntscli_cloud_lib.automator import DeviceIdentifier, GetTestPlanRequestOptions
from ntscli_cloud_lib.stateful_session import stateful_session_mgr

# Implementation libs
from ntsjson import cached_test_plan
from ntsjson.functions import get_user_requested_device, nonblock_target_write, set_log_levels_of_libs
from ntsjson.log import logger


def get_plan_impl(rae: str, esn: str, ip: str, serial: str, configuration: str, testplan: BytesIO, playlist: str, type_: Optional[str]):
    set_log_levels_of_libs()
    target: DeviceIdentifier = get_user_requested_device(esn, ip, rae, serial)

    with stateful_session_mgr(**dict(configuration=configuration, **target.to_dict())) as stateful:
        options = GetTestPlanRequestOptions(test_plan_type="playlist", playlist_id=playlist) if playlist else GetTestPlanRequestOptions(test_plan_type="testplan")
        stateful.get_test_plan(options=options, type_=type_)
        plan_as_str: str = stateful.plan_request.to_json(indent=4)
        nonblock_target_write(testplan, plan_as_str)
        try:
            # cache it for later use
            cached_plan_path = cached_test_plan.path(target)
            with cached_plan_path.open("w") as plan_cache_file:
                plan_cache_file.write(plan_as_str)
            logger.info(f"test plan cached to {str(cached_plan_path)}")
        except OSError:
            logger.error("We were unable to cache the test plan to disk for later use, but this should not impact results.")
