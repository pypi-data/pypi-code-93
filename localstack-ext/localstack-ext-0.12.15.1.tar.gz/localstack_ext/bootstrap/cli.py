import json
import re

from docopt import docopt
from localstack import config
from localstack.utils.common import format_bytes, truncate

from localstack_ext import constants as ext_constants
from localstack_ext.bootstrap import auth


def cmd_login(argv, args):
    """
    Usage:
      localstack login [options]

    Options:
      --provider=<>           OAuth provider for login (default: github)
      --username=<>           OAuth username for login
    """
    args.update(docopt(cmd_login.__doc__.strip(), argv=argv))

    try:
        provider = args["--provider"] or "internal"
        auth.login(provider, args["--username"])
        print("Successfully logged in.")
    except Exception as e:
        raise Exception("Authentication error: %s" % e)


def cmd_logout(argv, args):
    """
    Usage:
      localstack logout
    """
    args.update(docopt(cmd_logout.__doc__.strip(), argv=argv))
    auth.logout()
    print("Successfully logged out.")


def cmd_ci(argv, args):
    """
    Usage:
      localstack ci <subcommand> [options]

    Commands:
      init                  Initialize CI configuration for a new repository
      repos                 List continuous integration repositories

    Options:
      --provider=<>         CI provider (default: travis)
      --repo=<>             Repository identifier
      --token=<>            API access token for CI provider
    """
    args.update(docopt(cmd_ci.__doc__.strip(), argv=argv))

    if args["<subcommand>"] == "repos":
        provider = args["--provider"] or "travis"
        result = auth.get_ci_repos(provider)
        print(result)
    elif args["<subcommand>"] == "init":
        provider = opt_params(args, ["--provider"]) or "travis"
        repo, token = mand_params(args, ["--repo", "--token"])
        auth.init_ci_repo(repo, token, provider=provider)
        print(repo, token)


def cmd_config(argv, args):
    """
    Usage:
      localstack config [ <key> ]
      localstack config <key> <value>

    Arguments:
      <key>             Key of configuration property to read or write
      <value>           Value of configuration property to write
    """
    args.update(docopt(cmd_config.__doc__.strip(), argv=argv))

    if args["<value>"]:
        auth.set_user_config(args["<key>"], args["<value>"])
        print("Successfully updated configuration value")
    else:
        result = auth.retrieve_user_config()
        if args["<key>"]:
            all_values = result
            result = {}
            for key, value in all_values.items():
                if re.match(args["<key>"], key):
                    result[key] = value
        print(json.dumps(result, indent=4))


def cmd_daemons(argv, args):
    """
    Usage:
      localstack daemons [ <subcommand> ]

    Commands:
      start        Start local daemon processes
      stop         Stop local daemon processes
    """
    args.update(docopt(cmd_daemons.__doc__.strip(), argv=argv))

    from localstack_ext.bootstrap import local_daemon

    if args["<subcommand>"] in [None, "start"]:
        print("Starting local daemons processes ...")
        local_daemon.start_in_background()
    elif args["<subcommand>"] in ["stop"]:
        print("Stopping local daemons processes ...")
        local_daemon.kill_servers()


def cmd_pod(argv, args):
    """
    Usage:
      localstack pod <subcommand> [ <name> ]

    Commands:
      push <name>      Push the state of a local cloud pod
      pull <name>      Pull the state to launch a cloud pod locally
    """
    args.update(docopt(cmd_pod.__doc__.strip(), argv=argv))
    from localstack_ext.bootstrap import (
        pods_client,  # leave import here to avoid dependency conflict
    )

    if args["<subcommand>"] == "push":
        print("Pushing local persistence state to backend ...")
        pods_client.push_state(args["<name>"], args)
    elif args["<subcommand>"] == "pull":
        print("Pulling persistence state from backend ...")
        pods_client.pull_state(args["<name>"], args)
    elif args["<subcommand>"] == "list":
        print("Fetching list of pods from server ...")
        result = pods_client.list_pods(args)
        # print('result', result)
        headers = {
            "pod_name": "Name",
            "backend": "Backend",
            "url": "URL",
            "size": "Size",
            "state": "State",
        }
        print_table(result, headers=headers, formats={"size": format_bytes})


def cmd_status(argv, args):
    from localstack.utils.cli import print_status

    print_status()
    print("\nExtended Details:")
    print("------------------")
    print("Pro Version:\t\t%s" % ext_constants.VERSION)
    # at this point we can assume that the API key has been validated...
    print("API Key:\t\tvalidated")


def register_commands():
    config.CLI_COMMANDS["daemons"] = {
        "description": "Manage local daemon processes",
        "parameters": [],
        "function": cmd_daemons,
    }
    config.CLI_COMMANDS["pod"] = {
        "description": "Manage state of local cloud pods",
        "parameters": [],
        "function": cmd_pod,
    }
    if "status" in config.CLI_COMMANDS:
        config.CLI_COMMANDS["status"]["function"] = cmd_status

    config.CLI_COMMANDS["login"] = {
        "description": "Log in with your account credentials",
        "function": cmd_login,
    }
    config.CLI_COMMANDS["logout"] = {
        "description": "Log out and delete any session tokens",
        "function": cmd_logout,
    }

    # TODO enable commands below?
    return

    config.CLI_COMMANDS["config"] = {
        "command": "  localstack config",
        "description": "Manage configuration values",
        "parameters": [],
        "function": cmd_config,
    }
    config.CLI_COMMANDS["ci"] = {
        "description": "Manage continuous integration repositories and settings",
        "function": cmd_ci,
    }


# -----------------
# HELPER FUNCTIONS
# -----------------


def mand_params(args, names=[]):
    return get_params(args, names, mandatory=True)


def opt_params(args, names=[]):
    return get_params(args, names, mandatory=False)


def get_params(args, names=[], mandatory=True):
    result = ()
    for name in names:
        value = None
        if name in args:
            value = args[name]
        if not value and mandatory:
            raise Exception("Please provide %s=... parameter" % name)
        result += (value,)
    if len(result) == 1:
        return result[0]
    return result


def print_table(data_list, headers=[], formats={}):
    from tabulate import tabulate

    if not isinstance(data_list, list):
        raise Exception("Non-list input cannot be rendered as table: %s" % data_list)
    formats = formats or {}
    data_list = [i if isinstance(i, dict) else {"value": i} for i in data_list]
    # prepare headers
    if isinstance(headers, dict):
        headers = [{"key": k, "name": v} for k, v in headers.items()]
    # build column metadata
    columns = headers
    if not columns:
        columns = []
        for row in data_list:
            for key in row.keys():
                if key not in columns:
                    columns.append(key)
    for idx in range(len(columns)):
        column = columns[idx]
        columns[idx] = column if isinstance(column, dict) else {"key": column, "name": column}

    # build rows
    def _format(row, key):
        value = row.get(key)
        formatter = formats.get(key)
        if formatter:
            return formatter(value)
        if not value:
            return value
        return truncate(str(value), max_length=30)

    rows = [[_format(row, h["key"]) for h in columns] for row in data_list]
    headers = [col["name"] for col in columns]
    result = tabulate(rows, headers=headers)
    print(result)
