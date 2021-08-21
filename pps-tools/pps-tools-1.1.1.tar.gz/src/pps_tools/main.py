import argparse
import sys
import time

from . import __version__
from . import data
from . import io

EDGE_FMT = "{name} {count} @ {time:0.9f}"


def _mode_str(mode):
    return ", ".join(desc for bv, desc in data.MODE_BITS if mode & bv)


def fetch(pps_file, timeout=None):
    """Fetch events from the PPS device."""
    capabilities = pps_file.get_cap()

    do_sleep = False
    if capabilities & data.PPS_CANWAIT == 0:
        print("Warning: Cannot wait on PPS event. Will sleep instead.")
        do_sleep = True

    while True:
        event = pps_file.fetch(timeout=timeout)
        edges = []

        if event['mode'] & data.PPS_CAPTUREASSERT:
            edges.append(EDGE_FMT.format(
                name="assert",
                count=event['assert_seq'],
                time=event['assert_time']))

        if event['mode'] & data.PPS_CAPTURECLEAR:
            edges.append(EDGE_FMT.format(
                name="clear",
                count=event['clear_seq'],
                time=event['clear_time']))

        print(" ; ".join(edges))
        if do_sleep:
            time.sleep(1)


def info(pps_file):
    """Print out the current configuration for the given PPS device."""
    cap = pps_file.get_cap()
    cap_dict = data.cap_to_dict(cap)
    par = pps_file.get_params()
    mode_str = _mode_str(par['mode'])

    print("API Version         : {}".format(par['api_version']))
    print("Assert Offset       : {}".format(par['assert_offset']))
    print("Clear Offset        : {}".format(par['clear_offset']))
    print("Current Mode        : 0x{:02x} - {}".format(par['mode'], mode_str))
    print("Capabilities        : 0x{}".format(cap))
    for k, v in cap_dict.items():
        print("  {:18}: {}".format(k, v))


def params(pps_file, **kwargs):
    """Get and update the configuration for the given PPS device.

    This will print the updated configuration at the end.
    """
    par = pps_file.get_params()

    # Conditionally update the parameters
    updated = False
    for name, value in kwargs.items():
        if value is not None and par[name] != value:
            par[name] = value
            updated = True

    # Only try to set if updated (may be blocked by permissions)
    if updated:
        pps_file.set_params(**par)

    # Get latest state and print
    info(pps_file)


def main(args=None):
    if args is None:
        args = sys.argv

    parser = argparse.ArgumentParser("pps-tools")
    parser.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version and exit"
    )

    subparsers = parser.add_subparsers()

    # fetch command
    p_fetch = subparsers.add_parser(
        "fetch",
        help="Fetch pulse events and print out information."
    )
    p_fetch.add_argument(
        "--timeout", "-t", type=float, default=None,
        help="Timeout for each fetch in seconds."
    )
    p_fetch.add_argument("pps_path", type=str, help="PPS device file to open")
    p_fetch.set_defaults(func=fetch)

    # params command
    p_params = subparsers.add_parser(
        "params",
        help="Read and/or set parameters for the given PPS device."
    )
    p_params.add_argument(
        "--mode", "-m", type=int, default=None,
        help="Integer mode value. See the RFC Mode bit definitions."
    )
    p_params.add_argument(
        "--api_version", "-v", type=int, default=None,
        help="Control the API version (doesn't really do anything)"
    )
    p_params.add_argument(
        "--assert_offset", "-a", type=float, default=None,
        help="Assert offset, in seconds (floating point)"
    )
    p_params.add_argument(
        "--clear_offset", "-c", type=float, default=None,
        help="Clear offset, in seconds (floating point)"
    )
    p_params.add_argument("pps_path", type=str, help="PPS device file to open")
    p_params.set_defaults(func=params)

    # Parse and run
    args = parser.parse_args(args[1:])
    arg_dict = args.__dict__

    if arg_dict.pop("version", False):
        print("pps-tools v{}".format(__version__))
        exit(0)

    func = arg_dict.pop("func", None)
    pps_path = arg_dict.pop("pps_path", None)

    if func is None or pps_path is None:
        parser.print_help()
        exit(2)

    with io.PpsFile(pps_path) as pps_file:
        func(pps_file, **arg_dict)
