#!/usr/bin/env python3
import argparse
import json

from .api import get_dbus_proxy, get_proxy_state


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--field", help="select a single field to read")
    args = parser.parse_args(argv)

    proxy = get_dbus_proxy()
    state = get_proxy_state(proxy)

    if args.field is None:
        print(json.dumps(state, indent=4))
    else:
        print(state[args.field])


if __name__ == "__main__":
    main()
