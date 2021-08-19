import sys
import time

from ntscli_cloud_lib.automator import DeviceIdentifier, HttpLikeStatusResponse
from ntscli_cloud_lib.stateful_session import stateful_session_mgr

# Implementation libs
from ntsjson.functions import get_user_requested_device, nonblock_target_write, set_log_levels_of_libs
from ntsjson.log import logger


def cancel_impl(rae: str, esn: str, ip: str, serial: str, configuration: str, save_to, no_wait: bool):
    """
    Cancel any pending tests for a specified device.
    """
    set_log_levels_of_libs()
    target: DeviceIdentifier = get_user_requested_device(esn, ip, rae, serial)

    with stateful_session_mgr(**dict(configuration=configuration, **target.to_dict())) as session:
        nonblock_target_write(save_to, session.cancel().to_json(indent=4))

        # by default, we wait for the device to be idle
        if not no_wait:

            def target_is_my_target(target: DeviceIdentifier) -> bool:
                return target.esn == esn or target.ip == ip or target.serial == serial

            for i in range(30):
                resp, raw = session.status(device=session.device)
                resp: HttpLikeStatusResponse

                my_sessions = [elt for elt in resp.body.sessions if target_is_my_target(elt.target)]
                if len(my_sessions) == 0:
                    logger.debug("no test sessions to wait on")
                    sys.exit(0)
                for s in my_sessions:
                    if s.status == "idle":
                        logger.debug("device is no longer busy")
                        sys.exit(0)
                    else:
                        logger.debug("waiting for busy device")
                        time.sleep(1)
            logger.error("The device never went idle after a cancel request.")
            sys.exit(1)
    # if we are not waiting, just exit cleanly here
    sys.exit(0)
