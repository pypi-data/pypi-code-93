import argparse
import os
import logging

from partialedge.exception.ped_exception import PartialEdgeDrawingException
from partialedge.algorithm import ped_run as ts

parser = argparse.ArgumentParser(description="determine maximum ink partial edge drawing of a graph drawing or a set of graph drawings")

parser.add_argument("--mode", action="store", choices=["single", "set", "dir"], help="process a single input file, a file containing a set of graph drawings, or a directory of set files")

parser.add_argument("--symmetric", action="store_true", help="input will be processed as symmetric PED problem")
parser.add_argument("--homogeneous", action="store_true", help="input will be processed as homogeneous PED problem")

parser.add_argument("--json", "-j", action="store", dest="json_dir", help="store result data at the given directory")
parser.add_argument("--image", "-i", action="store", dest="image_dir", help="store result image at the given directory")
parser.add_argument("--include-source", "-s", action="store_true", dest="include_source", help="store source graph image with the result image")
parser.add_argument("--verbose", "-v", action="count", dest="verbosity", default=0, help="v count determines logging verbosity level")

parser.add_argument("input", action="store", help="path to input file or directory depending on mode")


def run_ped():
    args = parser.parse_args()

    logging.basicConfig(format="%(message)s\n", level=logging.INFO)
    ped_logger = logging.getLogger("ped_logger")
    ped_logger.setLevel(logging.INFO - args.verbosity)

    if not args.symmetric and args.homogeneous:
        ped_logger.error("MaxHPED problem not supported")
    else:
        if args.mode == "single":
            if os.path.isfile(args.input):
                ped_logger.log(logging.INFO, "running {} in single file mode".format(args.input))
                ts.run_single_execution(args.input, args.symmetric, args.homogeneous, ped_logger, args.json_dir, args.image_dir, args.include_source)
            else:
                raise PartialEdgeDrawingException("single file mode requires a path to a json file containing valid graph data as input")

        elif args.mode == "set":
            if os.path.isfile(args.input):
                ped_logger.log(logging.INFO, "running {} in test set mode".format(args.input))
                ts.run_set_execution(args.input, args.symmetric, args.homogeneous, ped_logger, args.json_dir, args.image_dir, args.include_source)
            else:
                raise PartialEdgeDrawingException("set mode requires a path to a json file containing valid data of named graphs as input")

        elif args.mode == "dir":
            if os.path.isdir(args.input):
                ped_logger.log(logging.INFO, "running {} in directory mode".format(args.input))
                ts.run_dir_execution(args.input, args.symmetric, args.homogeneous, ped_logger, args.json_dir, args.image_dir, args.include_source)
            else:
                raise PartialEdgeDrawingException("dir mode requires a path to a directory containing several json files in set mode as input")

        else:
            raise PartialEdgeDrawingException("mode {} not supported".format(args.mode))


if __name__ == "__main__":
    run_ped()
