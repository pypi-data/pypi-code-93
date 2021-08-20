import sys

import colorama

from copy import deepcopy
from itertools import filterfalse
from typing import Optional

from ntscli_cloud_lib.automator import DeviceIdentifier, GetTestPlanRequestOptions
from ntscli_cloud_lib.stateful_session import stateful_session_mgr, StatefulSession

# Implementation libs
from ntsjson import MISSING_TARGET_ERROR
from ntsjson.functions import get_user_requested_device, set_log_levels_of_libs, choose_destination_device
from ntsjson.log import logger
from ntsjson.monitors import BlockMainThreadUntilCompleteMonitor,\
    PrintResultsWhenDoneClass,\
    PrintResultsWhileRunningClass


def eyepatch_check_calibration_impl(
        rae: str,
        esn: str,
        ip: str,
        serial: str,
        configuration: str,
        type_: Optional[str]):
    set_log_levels_of_libs()
    target: DeviceIdentifier = get_user_requested_device(esn, ip, rae, serial)

    with stateful_session_mgr(**dict(configuration=configuration, **target.to_dict())) as stateful:
        # Get the list of calibration tests.
        options = GetTestPlanRequestOptions(test_plan_type="calibration")
        stateful.get_test_plan(options=options, type_=type_)
        plan_as_str: str = stateful.plan_request.to_json(indent=4)
        logger.info(f"Calibration tests {str(plan_as_str)}")

    check_calibration_plan = get_check_calibration_test_plan(stateful.plan_request)
    session_target = choose_destination_device(check_calibration_plan, target)
    if not session_target:
        sys.exit(1)

    with stateful_session_mgr(**dict(configuration=configuration, **session_target.to_dict())) as session:
        session: StatefulSession

        session.plan_request = check_calibration_plan
        # create these whether or not we use them
        when_done_instance = PrintResultsWhenDoneClass(skip_download=False, result_file=sys.stdout)
        waiter = BlockMainThreadUntilCompleteMonitor()

        no_wait = False
        skip_print_after = False
        print_during = False

        if not no_wait:
            if not skip_print_after:
                session.status_watchers.append(when_done_instance)
            if print_during:
                session.status_watchers.append(PrintResultsWhileRunningClass(result_file=sys.stdout))
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

def get_check_calibration_test_plan(all_cal_tests):
    calibration_test_name = "EYEPATCH-CHECK-CALIBRATION"

    calibration_plan = deepcopy(all_cal_tests)
    calibration_plan.testplan.testcases[:] = filterfalse(
        lambda testcase: testcase.name != calibration_test_name,
        calibration_plan.testplan.testcases)

    # Have to add this to make sure the test doesn't stop for user prompts...
    calibration_plan.testplan.testcases[0].exec += f"&skipPrompt=true"

    return calibration_plan
