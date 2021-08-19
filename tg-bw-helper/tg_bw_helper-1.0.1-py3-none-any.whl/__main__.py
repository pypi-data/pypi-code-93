#!/usr/bin/env python
import argparse
import getpass
import os
import pathlib
import sys

from tg_bw_helper.bw_client import get_bw_pass_interactive


def run():
    parser = argparse.ArgumentParser(description="Get bitwarden password for particular entry.")
    parser.add_argument(
        "--bw-executable",
        type=str,
        help="path to bw executable",
        default=os.environ.get("TG_BW_AP_EXECUTABLE_PATH", "/usr/bin/bw"),
    )
    parser.add_argument(
        "--fallback-prompt",
        type=str,
        help="fallback (if bw executable does not exist) prompt for the password",
        default=os.environ.get("TG_BW_AP_FALLBACK_PROMPT", "Vault password: "),
    )
    parser.add_argument("--vault-item", type=str, help="vault item ID", required=True)
    parser.add_argument(
        "--vault-item-field",
        type=str,
        help="vault item field name, if not specified then password special field is used",
        required=False,
        default=None,
    )

    args = parser.parse_args()

    bw_executable_path = pathlib.Path(args.bw_executable)

    if bw_executable_path.exists():
        password = get_bw_pass_interactive(args.bw_executable, args.vault_item, args.vault_item_field)
    else:
        password = None

    if password is None:
        password = getpass.getpass(args.fallback_prompt)

    sys.stdout.write(password)


if __name__ == "__main__":
    run()  # pragma: no cover
