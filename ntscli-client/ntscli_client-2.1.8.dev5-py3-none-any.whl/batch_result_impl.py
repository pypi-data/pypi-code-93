import json
import sys

from ntscli_cloud_lib.automator import HttpLikeStatusResponse, StatusBody
from ntscli_cloud_lib.stateful_session import stateful_session_mgr
import requests

# Implementation libs
from ntsjson import MISSING_TARGET_ERROR
from ntsjson.functions import nonblock_target_write, set_log_levels_of_libs
from ntsjson.log import logger


def batch_result_impl(**kwargs):
    set_log_levels_of_libs()

    # if no device ID is set, stop early and loudly
    if not kwargs.get("esn", None) and not kwargs.get("ip", None) and not kwargs.get("serial", None):
        logger.critical(MISSING_TARGET_ERROR + ". You can get more general status with the status command.")
        sys.exit(1)

    with stateful_session_mgr(**kwargs) as session:

        # =====
        # latest!
        if kwargs["batch_id"] == "latest":
            resp, raw = session.status()
            resp: HttpLikeStatusResponse
            if resp is None or resp.status != 200:
                logger.error(f"Got an error retrieving status from the Automator:\n{resp}")

            if "esn" in kwargs and kwargs["esn"]:
                my_latest_session = [s for s in resp.body.sessions if s.target.esn == kwargs["esn"]]
                for ss in my_latest_session:
                    if ss.last_batch:
                        kwargs["batch_id"] = ss.last_batch
            elif "ip" in kwargs and kwargs["ip"]:
                my_latest_session = [s for s in resp.body.sessions if s.target.ip == kwargs["ip"]]
                for ss in my_latest_session:
                    if ss.last_batch:
                        kwargs["batch_id"] = ss.last_batch
            elif "serial" in kwargs and kwargs["serial"]:
                my_latest_session = [s for s in resp.body.sessions if s.target.serial == kwargs["serial"]]
                for ss in my_latest_session:
                    if ss.last_batch:
                        kwargs["batch_id"] = ss.last_batch

        if kwargs["batch_id"] == "latest":
            logger.error("There was no latest batch ID for that device. Printing all status instead.")
            del kwargs["batch_id"]

        resp, raw = session.get_result_for_batch_id(kwargs.get("batch_id"))
        resp: HttpLikeStatusResponse
        if kwargs.get("skip_download", False):
            result_str = json.dumps(raw, indent=4)
            nonblock_target_write(kwargs.get("save_to"), result_str)
        else:
            casted = resp.body
            if casted.running:
                logger.error("Not downloading full result set because the batch is still running.")
            else:
                if casted.results_url is None:
                    logger.error("No results URL was included with this batch result.")
                    sys.exit(1)

                logger.info("Downloading full report from URL in JSON response")
                # grab and unzip the url
                resp2 = requests.get(casted.results_url)
                try:
                    resp2.raise_for_status()
                except requests.HTTPError:
                    logger.error(
                        "We couldn't download the file for you. Perhaps the temporary URL expired, or the ID was not found. "
                        "You can still find results on NTS. Continuing analysis."
                    )
                    sys.exit(1)

                full_result_set: StatusBody = StatusBody().from_dict(value=resp2.json())
                nonblock_target_write(kwargs.get("save_to"), full_result_set.to_json(indent=4))
