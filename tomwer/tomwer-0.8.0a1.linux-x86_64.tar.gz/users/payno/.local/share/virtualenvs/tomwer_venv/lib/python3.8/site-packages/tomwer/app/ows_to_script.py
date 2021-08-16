#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import argparse
from pypushflow.representation.scheme.ows_parser import OwsParser
from pypushflow import Workflow
import tomwer.version
import pypushflow.version
import os

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


def _convert(scheme, output_file, overwrite):
    """

    :param scheme:
    :param scan:
    :param timeout:
    :return:
    """
    _logger.warning("translate {} to {}".format(scheme, output_file))

    if os.path.exists(output_file):
        if overwrite is True:
            os.remove(output_file)
        else:
            raise ValueError("{} already exists.".format(output_file))

    with open(output_file, "w+") as file_:
        file_.write(_dump_info_generation())

    workflow = Workflow.ProcessableWorkflow(scheme)
    converter = Workflow.Converter(workflow=workflow, output_file=output_file)
    converter.process()

    # set up workflow
    with open(output_file, mode="a") as file_:
        file_.write(_dump_executable_script_section())
    _logger.info(
        "translation finished. You can execute python {} [scan path] [[--entry]]".format(
            output_file
        )
    )


def _dump_info_generation():
    return (
        "# This file has been generated automatically using \n"
        "# pypushflow {} and tomwer {}\n".format(
            pypushflow.version.version, tomwer.version.version
        )
    )


def _dump_executable_script_section():
    return """
from tomwer.core.process.utils import IgnoreProcess

if __name__ == '__main__':
    import argparse
    import sys
    from tomwer.core.scan.scanfactory import ScanFactory
    from tomwer.core.scan.hdf5scan import HDF5TomoScan

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'scan_path',
        help='Data file to show (h5 file, edf files, spec files)')
    parser.add_argument(
        '--entry',
        default=None,
        help='An entry should be specify for hdf5 files')

    options = parser.parse_args(sys.argv[1:])
    if options.entry is None:
        scan = ScanFactory.create_scan_object(options.scan_path)
    else:
        scan = ScanFactory.create_scan_object(options.scan_path,
                                              entry=options.entry,
                                              accept_bliss_scan=True)
    if scan is None:
        raise ValueError('Given scan path is not recognized as a path'
                         'containing a scan')
    main(input_data=scan, channel='data')
    """


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "workflow_file",
        help="Path to the .ows file defining the workflow to process with the"
        "provided scan",
    )
    parser.add_argument("output_file", help="Output python file")
    parser.add_argument(
        "--overwrite",
        help="Overwrite output file if exists",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Set logging system in debug mode",
    )
    options = parser.parse_args(argv[1:])
    if not options.output_file.lower().endswith(".py"):
        options.output_file = options.output_file + ".py"
    # tune the log level
    log_level = logging.INFO
    if options.debug is True:
        log_level = logging.DEBUG

    for log_ in ("tomwer", "pypushflow"):
        logging.getLogger(log_).setLevel(log_level)

    scheme = OwsParser.scheme_load(options.workflow_file, load_handlers=True)
    _convert(
        scheme=scheme, output_file=options.output_file, overwrite=options.overwrite
    )


if __name__ == "__main__":
    main(sys.argv)
# convert an ows file to a script calling tomwer low level processes.
