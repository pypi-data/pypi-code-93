"""
Callable front-end to statically bound locators
"""
import argparse
import sys

from archive_ops.locators import *
from util_lib.version import bdrc_util_version

# Constant values, for dictionary
ENCODE_S3: str = "s3"
ENCODE_LAST_TWO: str = "two"
ENCODE_NULL: str = "null"

command_dispatch: {} = dict(
    {ENCODE_S3: r_s3,
     ENCODE_LAST_TWO: r_divmod_50_b_2,
     ENCODE_NULL: r_null}
)


def invoke_mapping_func(args: object) -> callable:
    """
    Derives the mapping algorithm from the command line argument
    :param args: parsed object
    :type args: ArgumentParser Parsed object
    :return: command_dispatch value, command_dispatch[ENCODE_LAST_TWO] if default
    """
    if args.two:
        return command_dispatch[ENCODE_LAST_TWO]
    if args.s3:
        return command_dispatch[ENCODE_S3]
    if args.null:
        return command_dispatch[ENCODE_NULL]
    #
    # Default
    #
    # replace this when new archive is in place
    return command_dispatch[ENCODE_NULL]


def locate_archive():
    parser = argparse.ArgumentParser(description="Provides mapping of archive names to paths")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-s", "--s3", action="store_true", help="Map to ENCODE_S3 storage (hexdigest[:2])")
    group.add_argument("-t", "--two", action="store_true",
                       help="Derive from last two characters of archive (default)")
    group.add_argument("-n", "--null", action="store_true", help="No Derivation - return input")
    parser.add_argument("root", type=str, help="parent of archive trees")
    parser.add_argument("archive", type=str, help="the name of the work")

    if "-v" in sys.argv or "--version" in sys.argv:
        print(bdrc_util_version())
        sys.exit(0)

    arg_obj: object = parser.parse_args()

    invoked_encoder = invoke_mapping_func(arg_obj)
    resolved_archive = invoked_encoder(arg_obj.root, arg_obj.archive)
    print(resolved_archive)


if __name__ == '__main__':
    locate_archive()
