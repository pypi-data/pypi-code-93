import atexit
from io import BytesIO
import json
import logging
import os
import platform
import re
import sys
import threading
from typing import Optional

import colorama
from furl import furl
from kaiju_mqtt_py import MqttPacket

# Implementation libs
from ntscli_cloud_lib.automator import DeviceIdentifier, TestCase, TestPlanRunRequest

from ntsjson import MISSING_TARGET_ERROR
from ntsjson.log import logger

if platform.system() != "Windows":
    import fcntl


def make_basic_options_dict(esn, ip, rae, serial, configuration="cloud"):
    """
    Make the boilerplate "form my options dict" go away.

    This is falling out of favor, as I'm finding myself double-converting.
    """

    target: DeviceIdentifier = get_target_from_env(ip, esn, serial)

    if not target.esn and not target.ip and not target.serial:
        logger.critical(MISSING_TARGET_ERROR)
        sys.exit(1)

    options = {"configuration": configuration}
    if rae:
        options["rae"] = rae
    if target.esn:
        options["esn"] = target.esn
    if target.ip:
        options["ip"] = target.ip
    if serial:
        options["serial"] = target.serial
    return options


def set_log_levels_of_libs():
    """Consolidate all interesting loggers to the same level as the local logger."""
    logging.basicConfig(stream=sys.stderr, level=logger.level)
    from ntscli_cloud_lib.log import logger as cloud_logger

    logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)

    cloud_logger.setLevel(logger.level)
    from kaiju_mqtt_py import KaijuMqtt

    KaijuMqtt.logger.setLevel(logger.level)


def analyze_mqtt_status_packet(packet: MqttPacket):
    print(json.dumps(packet.payload, indent=4))


write_lock = threading.Lock()


def nonblock_target_write(target_: BytesIO, s_: str):
    """
    Write and flush a string as utf-8

    Writing large segments of data to a stdout type stream can crash your app if you do it wrong.
    """

    def write_last(target: BytesIO, s: str):
        with write_lock:
            if platform.system() != "Windows":
                # make stdout/file a non-blocking file
                # this is apparently not possible like this in Windows, so we're putting a band-aid on it for today
                fd = target.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

            to_write = s.encode("utf-8")
            written = 0
            while written < len(s):
                try:
                    written = written + os.write(target.fileno(), to_write[written:])
                except BlockingIOError:
                    # logger.debug("HEY DAVE! HERE!")
                    continue
                except OSError as e:
                    logger.debug(e)

            try:
                written + os.write(target.fileno(), "\n".encode("utf-8"))
            except BlockingIOError:
                logger.debug("HEY DAVE! HERE! ANOTHER ONE!")
            except OSError as e:
                logger.debug(e)

            target.flush()

    atexit.register(write_last, target=target_, s=s_)


def get_target_from_env(ip, esn, serial) -> DeviceIdentifier:
    """
    Form a DeviceIdentifier with defaults from the env.

    :return:
    """
    if not ip and not esn and not serial:
        di = DeviceIdentifier(esn=os.getenv("ESN"), ip=os.getenv("DUT_IP"), serial=os.getenv("DUT_SERIAL"))
    else:
        return DeviceIdentifier(esn=esn, ip=ip, serial=serial)
    return di


def get_user_requested_device(esn, ip, rae, serial, device_id_required=True) -> DeviceIdentifier:
    """
    Load the default device and config based on CLI params and env vars.

    :param device_id_required:
    :param esn:
    :param ip:
    :param rae:
    :param serial:
    :param configuration:
    :return:
    """

    target: DeviceIdentifier = get_target_from_env(ip, esn, serial)
    target.rae = rae
    if device_id_required and (not target.esn and not target.ip and not target.serial):
        logger.critical(MISSING_TARGET_ERROR)
        sys.exit(1)

    return target


def filter_testcases(
    batch: str,
    categories: str,
    chosen_plan: TestPlanRunRequest,
    remove_eyepatch_tests: bool,
    names: str,
    names_re: str,
    tags: str,
    maxnrdjs: bool = False,
    instrumentation_areas: Optional[str] = None,
    trace_areas: Optional[str] = None,
    branch: Optional[str] = None,
    pull_request: Optional[str] = None,
    commit_hash: Optional[str] = None,
):
    """
    Common filter command for both run and filter commands.

    :param trace_areas:
    :param instrumentation_areas:
    :param maxnrdjs: Add the "max nrd js" arg
    :param branch: Use this named branch on source service
    :param pull_request: Use this PR branch on source service
    :param commit_hash: Use this commit branch on source service
    :param batch: batch name to add to chosen_plan. how did that get here?
    :param categories: CSV string. Only include tests in any of these categories.
    :param chosen_plan: The plan to modify.
    :param remove_eyepatch_tests: exclude eyepatch tagged tests
    :param names: CSV string. Only include tests with any of these exact names.
    :param names_re: only include tests whose names match this regex.
    :param tags: CSV string. Only include tests with any of these exact names.
    :return:
    """
    # =====
    logger.info(
        f"Before editing, test plan included {colorama.Fore.BLUE}{len(chosen_plan.testplan.testcases)}{colorama.Style.RESET_ALL} tests."
    )
    if batch is not None:
        chosen_plan.testplan.batch_name = batch
    # add a name filter
    if names:
        logger.info(f"Removing tests with names not in {names} at the user's request.")
        nlist = names.split(",")
        chosen_plan.testplan.testcases = [elt for elt in chosen_plan.testplan.testcases if elt.name in nlist]
    # add a name regex filter
    if names_re:
        logger.info(f"Removing tests with names not matching {names_re} at the user's request.")
        try:
            pattern = re.compile(names_re)
            chosen_plan.testplan.testcases = [elt for elt in chosen_plan.testplan.testcases if pattern.match(elt.name)]
        except re.error:
            logger.critical("Could not compile your regex.")
            sys.exit(1)
    # add a category filter
    if categories:
        logger.info(f"Removing tests with categories not in {categories} at the user's request.")
        clist = categories.split(",")
        if len(clist) > 0:
            chosen_plan.testplan.testcases = [elt for elt in chosen_plan.testplan.testcases if elt.category in clist]
    if tags:
        logger.info(f"Removing tests without any of the tags in {tags} at the user's request.")
        user_tag_set = set(tags.split(","))
        if len(user_tag_set) > 0:
            chosen_plan.testplan.testcases = [
                elt for elt in chosen_plan.testplan.testcases if elt.tags if len(set(elt.tags.split(",")).intersection(user_tag_set)) > 0
            ]
    if remove_eyepatch_tests:
        logger.info("Removing EyePatch tests.")
        chosen_plan.testplan.testcases = [
            elt
            for elt in chosen_plan.testplan.testcases
            if (elt.tags is None or (elt.tags is not None and "batch_ep" not in elt.tags.split(",")))
        ]
    # BUT make sure you didn't remove -all- the tests.
    if len(chosen_plan.testplan.testcases) == 0:
        logger.critical(
            "We removed all the tests from the test plan. Instead of waiting for the "
            "Automator to tell us the test plan was empty, we will abort here."
        )
        sys.exit(1)

    if maxnrdjs or instrumentation_areas or trace_areas:

        def update_test(test: TestCase):
            url = furl(test.exec)
            if maxnrdjs:
                logger.debug("Setting max nrdjs on each test")
                url.args["nrdjsMax"] = "true"  # explicit js true, not bool-python-True
            if instrumentation_areas:
                logger.debug("Setting instrumentation area in each test")
                url.args["instareas"] = instrumentation_areas
            if trace_areas:
                logger.info("Setting trace area in each test")
                # see NewWsHandler.js in devicetests repo for parser
                # trace_areas is csv splittable: FOO:info,BAR:debug
                # each area is either THING or THING:level: GRAPHICS:info
                # for the record: I'm checking NONE of that.
                url.args["logtypes"] = trace_areas
                # url.query["loglevel"] = "debug"  # adjustable, but whatever

            test.exec = str(url)

        _ = [update_test(elt) for elt in chosen_plan.testplan.testcases]

    if branch or pull_request or commit_hash:
        new_branch_url = furl("https://source.dta.netflix.com/nrdp/devicetests")

        if branch:
            # branch/
            # 5.2
            new_branch_url.path.add("branch")
            new_branch_url.path.add(branch)
            chosen_plan.testplan.branch = str(new_branch_url)
        elif pull_request:
            # pull_requests/
            # 416
            new_branch_url.path.add("pull_requests")
            new_branch_url.path.add(pull_request)
            chosen_plan.testplan.branch = str(new_branch_url)
        elif commit_hash:
            # commits/
            # ee5ccee573385028aca472dfa2e38a843cf94084
            new_branch_url.path.add("commits")
            new_branch_url.path.add(commit_hash)

        # automator currently adds nrdptest and appends the relative URL
        # we just need to send the URL to the branch root
        chosen_plan.testplan.branch = str(new_branch_url)

    logger.info(
        f"After editing, the test plan included {colorama.Fore.BLUE}{len(chosen_plan.testplan.testcases)}{colorama.Style.RESET_ALL} "
        f"tests with device target '{chosen_plan.target.to_json()}'. "
    )


def choose_destination_device(chosen_plan: Optional[TestPlanRunRequest], target: DeviceIdentifier) -> Optional[DeviceIdentifier]:
    """
    Choose the final destination of the run command.

    The target device is:
    A device specified by any CLI args, or
    A device specified by any ENV vars, or
    A device in the existing test plan file, or
    Nothing

    :param chosen_plan: A source plan read from file, if provided by the user
    :param target: the device loaded from the CLI + env vars
    :return: The destination we should use, or None
    """

    # =====
    # The target of the Automator session is:
    session_target: Optional[DeviceIdentifier] = None

    # . the device in the existing test plan file, if any
    if chosen_plan:
        session_target = chosen_plan.target
    # . replaced by the default env vars for the target
    # . replaced by any cli args the user provides to replace the env vars
    if target.rae and (target.esn or target.ip or target.serial):
        session_target = target
        # explicitly update the test plan target only if the user has provided an alternative
        if chosen_plan:
            chosen_plan.target = target
            logger.info("Replacing the test plan target at the user's request with:")
            logger.info(chosen_plan.target.to_json())
    # if there is no target after all this, we should just stop
    if not session_target:
        logger.critical(
            f"{MISSING_TARGET_ERROR}. You may also provide --testplan with a valid device "
            "identifier in a test plan file."
            " Unable to determine the target RAE and device based on CLI args, test plan "
            "defaults and caches, or env vars."
        )
    # =====
    return session_target
