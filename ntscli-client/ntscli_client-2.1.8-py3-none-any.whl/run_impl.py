import json
from json import JSONDecodeError
import platform
import sys
from typing import Optional, TextIO

import colorama
from ntscli_cloud_lib.automator import DeviceIdentifier, TestPlanRunRequest
from ntscli_cloud_lib.stateful_session import stateful_session_mgr, StatefulSession

# Implementation libs
from ntsjson import cached_test_plan
from ntsjson.functions import filter_testcases, get_user_requested_device, set_log_levels_of_libs, choose_destination_device
from ntsjson.log import logger
from ntsjson.monitors import BlockMainThreadUntilCompleteMonitor, PrintResultsWhenDoneClass, PrintResultsWhileRunningClass

if platform.system() != "Windows":
    import fcntl
    from os import O_NONBLOCK


def run_impl(
    rae,
    esn,
    ip,
    serial,
    no_wait: bool,
    testplan: TextIO,
    batch: str,
    names: str,
    names_re: str,
    force_remove_eyepatch: bool,
    force_keep_eyepatch: bool,
    print_during: bool,
    skip_print_after: bool,
    categories: Optional[str],
    tags: Optional[str],
    configuration: str,
    result_file: Optional[TextIO],
    max_nrdjs: bool = False,
    instrumentation_areas: Optional[str] = "",
    trace_areas: Optional[str] = "",
    branch: Optional[str] = "",
    pull_request: Optional[str] = "",
    commit_hash: Optional[str] = "",
):
    set_log_levels_of_libs()
    target = get_user_requested_device(esn, ip, rae, serial, device_id_required=False)

    if platform.system() != "Windows":
        # make stdin a non-blocking file so the process does not hang
        # this is apparently not possible like this in Windows, so we're putting a band-aid on it for today
        fd = testplan.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | O_NONBLOCK)

    try:
        chosen_plan: Optional[TestPlanRunRequest] = get_plan_if_found(target, testplan)
    except JSONDecodeError:
        sys.exit(1)

    session_target = choose_destination_device(chosen_plan, target)
    if not session_target:
        sys.exit(1)

    with stateful_session_mgr(**dict(configuration=configuration, **session_target.to_dict())) as session:
        session: StatefulSession

        if chosen_plan is not None:
            session.plan_request = chosen_plan

        else:
            session.get_test_plan()  # stored in the session at .plan_request
            try:
                # cache it for later use
                cached_plan_path = cached_test_plan.path(session.device)
                with cached_plan_path.open("w") as plan_cache_file:
                    plan_cache_file.write(session.plan_request.to_json(indent=4))
                logger.info(f"test plan cached to {str(cached_plan_path)}")
            except OSError:
                logger.error("We were unable to cache the test plan to disk for later use, but this should not impact results.")

        should_remove_eyepatch_tests = should_remove_eyepatch_tests_decision(force_remove_eyepatch, force_keep_eyepatch, rae, session)

        filter_testcases(
            batch=batch,
            categories=categories,
            chosen_plan=session.plan_request,
            remove_eyepatch_tests=should_remove_eyepatch_tests,
            names=names,
            names_re=names_re,
            tags=tags,
            maxnrdjs=max_nrdjs,
            instrumentation_areas=instrumentation_areas,
            trace_areas=trace_areas,
            branch=branch,
            pull_request=pull_request,
            commit_hash=commit_hash,
        )

        # create these whether or not we use them
        when_done_instance = PrintResultsWhenDoneClass(skip_download=False, result_file=result_file)
        waiter = BlockMainThreadUntilCompleteMonitor()

        if not no_wait:
            if not skip_print_after:
                session.status_watchers.append(when_done_instance)
            if print_during:
                session.status_watchers.append(PrintResultsWhileRunningClass(result_file=result_file))
            # put this one last so we wait for analysis to finish in other classes
            session.status_watchers.append(waiter)

        logger.info(
            f"Running {colorama.Fore.BLUE}{len(session.plan_request.testplan.testcases)}{colorama.Style.RESET_ALL} "
            f"tests with device target '{session.device.to_json()}'. "
        )
        session.run_tests()

        if not no_wait:
            waiter.finished.wait()
            if when_done_instance.my_thread:
                pending_thread = when_done_instance.my_thread
                pending_thread.join(timeout=15.0)


def should_remove_eyepatch_tests_decision(force_remove_eyepatch: bool, force_keep_eyepatch: bool, rae: str, session: StatefulSession):
    """
    Should I remove eyepatch tests?

    :param force_remove_eyepatch: force removal of eyepatch tests
    :param force_keep_eyepatch: force keeping the eyepatch tests
    :param rae:
    :param session: must already be connected
    :return:
    """
    should_remove_eyepatch_tests = False
    if force_keep_eyepatch:
        return False
    if force_remove_eyepatch:
        return True
    try:
        if not session.plan_request.target.esn:
            # To see if a device has an EyePatch, we need its ESN. We take a brief detour to get as much information as we can about
            # the devices behind this RAE, so we can find the matching ESN.
            identifiers = session.get_device_list()
            if identifiers is None:
                logger.error(
                    "We were unable to get the list of device identifiers. This could be a connectivity issue, or the modules may "
                    "not be installed on the RAE."
                )
                raise ValueError("Skipping filtering of EyePatch tests.")
            if session.plan_request.target.ip:
                id_list = [_id for _id in identifiers if session.plan_request.target.ip == _id.ip]
            elif session.plan_request.target.serial:
                id_list = [_id for _id in identifiers if session.plan_request.target.serial == _id.serial]
            else:
                raise ValueError("Could not find an identifier for your device, we can not continue.")

            if len(id_list) == 0:
                raise ValueError("Could not find a matching device. Removing EyePatch tests.")

            # replace the device with the one straight off the RAE with more fields
            session.device = id_list[0]
            if not session.device.rae:
                session.device.rae = rae
            session.plan_request.target = session.device

            logger.info(f"Using ESN {session.device.esn} for EyePatch filter check.")

        if session.plan_request.target.esn:
            session.device = session.plan_request.target
            has_eyepatch = session.is_esn_connected_to_eyepatch()
            if not has_eyepatch:
                logger.info("Removing EyePatch tests, because this ESN does not have a configured EyePatch.")
                should_remove_eyepatch_tests = True
            else:
                logger.info("Not removing EyePatch tests because this device has a configured EyePatch.")
        else:
            logger.info("Removing EyePatch tests because we could not locate a matching device.")
            should_remove_eyepatch_tests = True

    except (ValueError, KeyError):
        logger.info("There was a problem getting the list of EyePatch connected devices, so the test plan will remove EyePatch tests")
        should_remove_eyepatch_tests = True

    return should_remove_eyepatch_tests


def get_plan_if_found(target: DeviceIdentifier, testplan: Optional[TextIO]) -> Optional[TestPlanRunRequest]:
    """
    Load user provided plan based on CLI input and defaults for a device.

    There are three paths through this:
    Plan loads from input and is returned
    No user input, plan loads from cache and is returned
    No user input, plan fails to load and JSONDecodeError is thrown
    No user input, nothing in cache, and None is returned

    :param target: Device to load cache for if nothing else works
    :param testplan: CLI input or stdin
    :return: TestPlanRunRequest or None
    """
    chosen_plan: Optional[TestPlanRunRequest] = None
    if testplan:
        logger.info("Attempting to read test plan from stdin or --testplan file")
        source_str: str = ""
        try:
            source_str = "".join([elt.strip() for elt in testplan.readlines()])
        except IOError:
            logger.info("There was no data to read")

        if not source_str and (target.rae or target.ip or target.esn or target.serial):
            logger.info("There was no user-provided data to read, looking in the cache")
            cached_plan_path = cached_test_plan.path(target)
            if cached_plan_path.exists():
                with cached_plan_path.open("r") as cached_plan_fp:
                    try:
                        source_str = cached_plan_fp.read()
                        logger.info("Cached test plan loaded.")
                    except json.JSONDecodeError as err:
                        logger.critical("The test plan cache file did not parse as JSON:")
                        logger.critical(err)
                        raise err
            else:
                logger.info("There was no valid cache for that device, continuing.")

        logger.info("Reading complete!")

        if source_str == "":
            logger.info(f"There was no data in {testplan.name}. Will attempt to get a test plan")
        else:
            try:
                chosen_plan = TestPlanRunRequest().from_dict(value=(json.loads(source_str)))
                # now you can inspect the test plan loaded from file to see if it looks like it's valid
                logger.info(f"Loaded {len(chosen_plan.testplan.testcases)} tests from file.")
            except (JSONDecodeError, KeyError, TypeError) as err:
                logger.critical("The source file did not parse as JSON:")
                logger.critical(err)
                raise err
    return chosen_plan
