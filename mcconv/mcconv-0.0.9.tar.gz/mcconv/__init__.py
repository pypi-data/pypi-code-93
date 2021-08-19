import argparse
import glob
import logging
import sys

from .detect import detect_mc_type
from .file_types import McFileTypes, parse_file_type
from .generic_reader import UnparsedTextEvent, GenericTextReader
from .hepmc_convert import hepmc_convert


# the default ccdb logger
logger = logging.getLogger("mcconv")


def shot_progress(event_index, evt):
    if event_index and event_index % 1000 == 0:
        logger.info(f"Events processed: {event_index:<10}")

def hepmc_convert_cli():
    """Main entry point of mcconv executable"""
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', nargs='+', help="File name (wildcards allowed)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debugging output. More than verbose")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output. Info level")
    parser.add_argument("-i", "--in-type", default="", help="Input file type: [auto, pythia6-bnl]")
    parser.add_argument("-f", "--format", default="3", help="HepMC format [2,3]")
    parser.add_argument("-r", "--report", default="report", help="Report folder (set blank for no report)")
    parser.add_argument("-o", "--output", default="output.hepmc", help="File name of resulting hepmc")
    parser.add_argument("-s", "--nskip", default=0, type=int, help="Number of events to skip")
    parser.add_argument("-p", "--nprocess", default=0, type=int, help="Number of events to process")

    args = parser.parse_args()

    # Configuring logger
    # create and set console handler
    stdout_handler = logging.StreamHandler()
    stdout_handler.stream = sys.stdout
    logger.addHandler(stdout_handler)

    # create stderr handler
    stderr_handler = logging.StreamHandler()
    stderr_handler.stream = sys.stderr
    stderr_handler.setLevel(logging.ERROR)
    logger.addHandler(stderr_handler)

    # Logger level from arguments
    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    # What files to process
    file_paths = []
    for user_input in args.inputs:
        # use Glob to convert something like some_dir/* to file names
        file_paths.extend([file_path for file_path in glob.glob(user_input)])

    # >oO DEBUG output
    logger.debug("Found files to process:")
    for file_path in file_paths:
        logger.debug(f"  {file_path}")

    input_file_type = parse_file_type(args.in_type)

    hepmc_convert(file_paths[0], args.output, input_file_type, args.format, shot_progress, args.nskip, args.nprocess)

if __name__ == '__main__':
    hepmc_convert_cli()
