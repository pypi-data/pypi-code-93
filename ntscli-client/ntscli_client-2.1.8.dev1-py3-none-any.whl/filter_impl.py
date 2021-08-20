from json import JSONDecodeError
import platform
import sys
from typing import Optional, TextIO

from ntscli_cloud_lib.automator import DeviceIdentifier, TestPlanRunRequest

# Implementation libs
from ntsjson.functions import filter_testcases, nonblock_target_write, set_log_levels_of_libs
from ntsjson.log import logger
from ntsjson.run_impl import get_plan_if_found

if platform.system() != "Windows":
    import fcntl
    from os import O_NONBLOCK


def filter_impl(
    rae,
    esn,
    ip,
    serial,
    testplan: TextIO,
    batch: str,
    names: str,
    names_re: str,
    eyepatch: bool,
    force_remove_eyepatch: bool,
    categories: Optional[str],
    tags: Optional[str],
    result_file: Optional[TextIO],
    max_nrdjs: bool = False,
    instrumentation_areas: Optional[str] = "",
    trace_areas: Optional[str] = "",
    branch: Optional[str] = "",
    pull_request: Optional[str] = "",
    commit_hash: Optional[str] = "",
):
    """Filter tests out of a test plan."""
    set_log_levels_of_libs()

    # don't use the standard loader because we don't want to pick up ENV vars
    target = DeviceIdentifier(rae=rae, ip=ip, esn=esn, serial=serial)

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

    if not chosen_plan:
        logger.critical(
            "Unable to find a source test plan. " "Please provide --testplan, cache a test plan for this device using nts get-plan"
        )
        sys.exit(1)

    if target.rae or target.ip or target.esn or target.serial:
        chosen_plan.target = target
        logger.info("Replacing the test plan target at the user's request with:")
        logger.info(chosen_plan.target.to_json())

    filter_testcases(
        batch=batch,
        categories=categories,
        chosen_plan=chosen_plan,
        remove_eyepatch_tests=eyepatch or force_remove_eyepatch,
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

    plan_as_str: str = chosen_plan.to_json(indent=4)
    nonblock_target_write(result_file, plan_as_str)
