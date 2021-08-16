#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import argparse
from pypushflow.representation.scheme.ows_parser import OwsParser
from tomwer.core.scan.scanfactory import ScanFactory
from pypushflow.Workflow import ProcessableWorkflow
from tomwer.core.scan.blissscan import BlissScan
import signal

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


def _exec(scheme, scan=None, timeout=None):
    """

    :param scheme:
    :param scan:
    :param timeout:
    :return:
    """
    # set up workflow
    if len(scheme.start_nodes()) == 0:
        _logger.warning("no start nodes found. Enable to process")
        return None
    mess = " ".join(
        (
            "start processing of scheme '{}'".format(scheme.title or "unknow"),
            "with",
            str(scan),
        )
    )
    _logger.info(mess)
    workflow = ProcessableWorkflow(scheme=scheme)

    # add SIGINT capture
    def signal_handler(sig, frame):
        _logger.warning("stop workflow execution on user request")
        workflow._end_actor.join(0)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    workflow._start_actor.trigger(("data", scan.to_dict()))
    workflow._end_actor.join(timeout)
    res = workflow._end_actor.out_data
    title = scheme.title or "unknow"
    _logger.info("workflow '{}' completed with {}".format(title, str(scan)))
    return res


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "workflow_file",
        help="Path to the .ows file defining the workflow to process with the"
        "provided scan",
    )
    parser.add_argument(
        "scan_path",
        help="Path to data to be processes (master file if come from an hdf5 "
        "acquisition or EDF files folder if come from an EDF acquisition)",
    )
    parser.add_argument(
        "--entry", default=None, help="An entry should be specify for hdf5 files"
    )
    parser.add_argument(
        "--timeout", default=None, help="Timeout for the workflow execution"
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Set logging system in debug mode",
    )
    options = parser.parse_args(argv[1:])
    if options.entry is not None:
        scan = ScanFactory.create_scan_object(
            options.scan_path, entry=options.entry, accept_bliss_scan=True
        )
        scans = (scan,)
    else:
        scans = ScanFactory.create_scan_objects(
            options.scan_path, accept_bliss_scan=True
        )
    if len(scans) > 1:
        _logger.info("More than one scan found. Will process every scans")

    # tune the log level
    log_level = logging.INFO
    if options.debug is True:
        log_level = logging.DEBUG

    for log_ in ("tomwer", "pypushflow"):
        logging.getLogger(log_).setLevel(log_level)

    scheme = OwsParser.scheme_load(options.workflow_file, load_handlers=True)
    for scan in scans:
        _exec(scheme=scheme, scan=scan, timeout=options.timeout)


if __name__ == "__main__":
    main(sys.argv)
