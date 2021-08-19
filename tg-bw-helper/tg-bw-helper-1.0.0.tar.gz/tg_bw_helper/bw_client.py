import getpass
import json
import os
import subprocess
import sys
import typing


class BWError(Exception):
    pass


class BWItemNotFound(BWError):
    pass


class BWMultipleItemsFound(BWError):
    pass


class BWFieldNotFound(BWError):
    pass


def get_bw_pass(
    bw_cli_path: str,
    entry_id: str,
    field_name: typing.Optional[str],
    bw_session_token: str,
) -> str:
    try:
        items = json.loads(
            subprocess.check_output(
                [bw_cli_path, "list", "items", "--search", entry_id],
                env={
                    **os.environ,
                    "BW_SESSION": bw_session_token,
                },
                text=True,
            )
        )
    except json.JSONDecodeError:
        items = []
    if len(items) == 0:
        raise BWItemNotFound()
    if len(items) > 1:
        raise BWMultipleItemsFound()

    item = items[0]

    if field_name is None:
        result = item.get("login", {}).get("password", None)
        if result is None:
            raise BWFieldNotFound()

        return result

    fields = item.get("fields", [])
    for field in fields:
        try:
            if field["name"] == field_name:
                return field["value"]
        except KeyError:
            pass

    raise BWFieldNotFound()


def get_bw_session_interactive(bw_cli_path: str) -> typing.Optional[str]:
    session_token = None
    tries = 0

    while session_token is None:
        if tries == 3:
            sys.stderr.write("Max retries exceeded.\n")
            return None

        master_password = getpass.getpass("Bitwarden master password: ")
        if not master_password:
            sys.stderr.write("Empty master password, falling back to asking vault password directly.\n")
            return None

        bw_cli = subprocess.Popen(
            [
                bw_cli_path,
                "unlock",
                "--raw",
            ],
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, errors = bw_cli.communicate(master_password)
        bw_cli.wait(10)

        if bw_cli.returncode == 0:
            session_token = output
        elif "you are not logged in" in errors.lower():
            sys.stderr.write("You are not logged into bitwarden. Use `bw login` and follow the instructions.\n")
            return None
        elif "invalid master password" in errors.lower():
            sys.stderr.write("Invalid master password.\n")
            tries += 1
        else:
            sys.stderr.write("Unknown bitwarden error.\n")
            sys.stderr.write(f"```{errors}```\n")
            return None

    return session_token


def get_bw_pass_interactive(bw_cli_path: str, entry_id: str, field_name: typing.Optional[str]) -> typing.Optional[str]:
    sys.stderr.write(f"Unlocking bitwarden to get {entry_id}:{field_name}\n")
    session_token = get_bw_session_interactive(bw_cli_path)
    if session_token is None:
        sys.stderr.write("Failed to get session token\n")
        return None

    try:
        return get_bw_pass(bw_cli_path, entry_id, field_name, session_token)
    except BWFieldNotFound:
        sys.stderr.write("Failed to get password from bw - invalid field\n")
    except BWItemNotFound:
        sys.stderr.write("Failed to get password from bw - invalid item\n")
    except BWMultipleItemsFound:
        sys.stderr.write("Failed to get password from bw - multiple items with this query, try using id.\n")

    return None
