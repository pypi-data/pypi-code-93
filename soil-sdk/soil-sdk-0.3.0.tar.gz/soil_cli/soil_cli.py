"""This module implements SOIL's Command LIne Interface"""
import argparse
import sys
import os
import json
import shutil
import getpass
import zipfile
from typing import Dict, Tuple, Optional
from json import JSONDecodeError  # Flake8...
import subprocess  # nosec
import virtualenv  # type: ignore
import requests
import yaml

parser = argparse.ArgumentParser(prog="soil")
subparsers = parser.add_subparsers(dest="command")

configure_cmd = subparsers.add_parser("configure", help="Configure SOIL-CLI")
configure_cmd.add_argument(
    "--reset", action="store_true", help="Reset the current configuration"
)

login_cmd = subparsers.add_parser("login", help="Login to configured soil instance")
login_cmd.add_argument("--user", type=str, help="User name or email of the user")
login_cmd.add_argument("--password", type=str, help="Password")

init_cmd = subparsers.add_parser(
    "init", help="Initialize a directory as a soil project"
)
init_cmd.add_argument(
    "dirname",
    nargs="*",
    metavar="DIR",
    default=".",
    help="Name of a directory to initialize as a soil app",
)


install_cmd = subparsers.add_parser(
    "install", help="Installs the provided packages to the soil instance."
)
install_cmd.add_argument(
    "--recursive",
    "-r",
    default=False,
    action="store_true",
    help="Recursive. Use a txt file instead.",
)
install_cmd.add_argument(
    "packages",
    nargs="+",
    metavar="PACKAGE[S]",
    help="Package[s] to install or a txt file if --recursive to install from.",
)

run_cmd = subparsers.add_parser(
    "run", help="Runs the provided module in the current soil project"
)
run_cmd.add_argument(
    "chapter",
    metavar="chapter",
    help="Chapter in soil.yml (setup, data, migration, ...)",
)
run_cmd.add_argument("module", metavar="module", help="Module of chapter in soil.yml")
run_cmd.add_argument(
    "module_args", nargs=argparse.REMAINDER, help="Arguments to be passed to the module"
)

test_cmd = subparsers.add_parser("test", help="Launches tests using SOIL. ")
test_cmd.add_argument(
    "test_args",
    nargs=argparse.REMAINDER,
    help="Arguments to be passed to the test command",
)


def save_environment(config: Dict, env: Dict) -> None:
    """
    Saves the environment keys to a file.
    The file is located in ~/.soil/soil.env and ~/.soil/:app_id/soil.env
    Where app_id is the app_id in the config.
    Notice that ~/.soil/soil.env will store the last login only.
    """

    try:
        os.makedirs(os.path.expanduser("~/.soil/" + config["auth_app_id"]))
    except FileExistsError:
        # directory already exists
        pass

    with open(os.path.expanduser("~/.soil/soil.env"), "w") as env_file:
        env_file.write(json.dumps(env, indent=4, sort_keys=True))

    shutil.copyfile(
        os.path.expanduser("~/.soil/soil.env"),
        os.path.expanduser("~/.soil/" + config["auth_app_id"] + "/soil.env")
    )


def get_soil_root(relpath: str):  # type: ignore
    """Checks if the current dir is under a soil environment and returns its root. Returns None otherwise."""

    path = os.path.abspath(relpath) + "/"

    while path != "/":
        path, _ = os.path.split(path)
        if "soil.yml" in os.listdir(path):
            return path

    return None


def soil_init() -> Tuple[Dict, Optional[Dict]]:
    """Loads configuration and environment."""

    project_root = get_soil_root(".")
    try:
        if project_root is None:
            raise FileNotFoundError("Project root not found.")
        with open(project_root + "/soil.conf") as config_file:
            config = json.loads(config_file.read())
    except FileNotFoundError:
        try:
            with open(os.path.expanduser("~/.soil/soil.conf"), "r") as config_file:
                config = json.loads(config_file.read())
        except (IOError, JSONDecodeError):
            if sys.argv[1] != "configure":
                try:
                    os.rename(
                        os.path.expanduser("~/.soil/soil.conf.bak"),
                        os.path.expanduser("~/.soil/soil.conf"),
                    )
                except IOError:
                    print(
                        "Can not load soil configuration. Plase run soil configure to configure it."
                    )
                    sys.exit()
            else:
                config = None
    try:
        with open(os.path.expanduser("~/.soil/soil.env"), "r") as env_file:
            env = json.loads(env_file.read())
        return config, env
    except (IOError, JSONDecodeError):
        if sys.argv[1] != "configure" and sys.argv[1] != "login":
            try:
                os.rename(
                    os.path.expanduser("~/.soil/soil.conf.bak"),
                    os.path.expanduser("~/.soil/soil.conf"),
                )
            except IOError:
                print(
                    "Can not load soil environment. Plase run soil configure to initialize it."
                )
                sys.exit()
        return config, None


def configure(args: argparse.Namespace, config: Dict) -> None:
    """
    Allows the user to provide the configuration parameters interactively and stores them into a file.
    """

    try:
        os.makedirs(os.path.expanduser("~/.soil/"))
    except FileExistsError:
        # directory already exists
        pass

    try:
        if args.reset:
            try:
                os.rename(
                    os.path.expanduser("~/.soil/soil.conf"),
                    os.path.expanduser("~/.soil/soil.conf.bak"),
                )
                os.rename(
                    os.path.expanduser("~/.soil/soil.env"),
                    os.path.expanduser("~/.soil/soil.env.bak"),
                )
            except FileNotFoundError:
                print(
                    "Seems there is no previous configuration. Performing a clean config..."
                )
                args.reset = False
        with open(os.path.expanduser("~/.soil/soil.conf"), "x") as config_file:
            config = {}
            config["soil_url"] = input(
                "Enter url of your soil instance: [https://soil.amalfianalytics.com]"
            ).replace(
                "\t", ""
            )  # nosec - Input is safe in python3
            if config["soil_url"] == "":
                config["soil_url"] = "https://soil.amalfianalytics.com"
            auth_url_msg = (
                "Enter authentication provider URL: [https://auth.amalfianalytics.com] "
            )
            config["auth_url"] = input(auth_url_msg).replace(
                "\t", ""
            )  # nosec - Input is safe in python3
            if config["auth_url"] == "":
                config["auth_url"] = "https://auth.amalfianalytics.com"
            config["auth_app_id"] = input("Enter your application id: ").replace(
                "\t", ""
            )  # nosec - Input is safe in python3
            config["auth_api_key"] = input("Enter your API key: ").replace(
                "\t", ""
            )  # nosec - Input is safe in python3
            config_file.write(json.dumps(config, indent=4, sort_keys=True))

        # Create the environment file
        with open(os.path.expanduser("~/.soil/soil.env"), "x") as env_file:
            env_file.write("{\n}")

        if args.reset:
            os.remove(os.path.expanduser("~/.soil/soil.conf.bak"))
            os.remove(os.path.expanduser("~/.soil/soil.env.bak"))

    except FileExistsError:
        if not args.reset:
            print("Soil already configured (Use --reset to reconfigure):\n")
            for option, value in config.items():
                print(option + ": " + value)


def login(args: argparse.Namespace, config: Dict, env: Optional[Dict]) -> None:
    """
    Authenticates to the authentication backend and stores the credentials (JWT) in the environment
    """

    print(f"Authenticating to {config['auth_url']} for app {config['auth_app_id']}...")

    if env is None:
        env = {}

    if args.user is not None and args.password is not None:
        username = args.user
        password = args.password
    else:
        if "auth" in env:
            username = input(
                "Username: ["
                + env["auth"]["user"].get(
                    "username", env["auth"]["user"].get("email", "")
                )
                + "]"
            )  # nosec - Input is safe in python3
            if username == "":
                username = env["auth"]["user"]["email"]
        else:
            username = input("Username: ")  # nosec - Input is safe in python3
        password = getpass.getpass()

    request_json = {
        "loginId": username,
        "password": password,
        "applicationId": config["auth_app_id"],
    }

    resp = requests.post(
        config["auth_url"] + "/api/login",
        headers={"Authorization": config["auth_api_key"]},
        json=request_json,
    )

    if resp.status_code == 200 or resp.status_code == 202:
        env["auth"] = json.loads(resp.content)
        save_environment(config, env)
        print(
            "Successfully logged in as "
            + env["auth"]["user"].get("username", env["auth"]["user"].get("email", ""))
            + "!"
        )
    elif resp.status_code == 404:
        print("The user was not found or the password was incorrect.")
        sys.exit(1)
    elif resp.status_code == 400:
        print(
            "Invalid parameters. Perhaps the api key %s or the app id %s are not correct."
            % (config["auth_api_key"], config["auth_app_id"])
        )
        sys.exit(1)
    else:
        print("Login failed with status code", resp.status_code)
        sys.exit(1)


def init(args: argparse.Namespace) -> None:
    """
    Initializes the current directory or the one provided as argument as a SOIL project by placing
    all the directory structure and creating a python virtual environment.
    """

    dirname = vars(args)["dirname"][0]

    if dirname != ".":
        try:
            os.mkdir(dirname)
        except FileExistsError:
            print("The directory " + dirname + " already exists")
            sys.exit()

    if get_soil_root(dirname):
        if dirname != ".":
            os.rmdir(dirname)
        print("This location is already a soil project")
        sys.exit()
    else:
        with zipfile.ZipFile(
            os.path.dirname(os.path.realpath(__file__)) + "/template.zip", "r"
        ) as template_zip:
            template_zip.extractall(os.path.abspath("./" + dirname))
        # copy soil.conf to local directory
        shutil.copyfile(
            os.path.expanduser("~/.soil/soil.conf"),
            os.path.abspath("./" + dirname + "/soil.conf"),
        )
        # create and activate the virtual environment
        virtualenv.cli_run([os.path.abspath("./" + dirname + "/.venv")])


def install(args: argparse.Namespace) -> None:
    """
    Placeholder install to install remote requirements.
    """
    print("This is a placeholder command to install remote requirements.")
    print("Install arguments:", args)
    # soil_root = get_soil_root('.')
    # if not soil_root:
    #     print("This folder is not initalized as a soil project. Please run soil init to initialize it.")
    #     sys.exit()

    # packages = vars(args)["packages"]

    # for package in packages:
    #     subprocess.check_call(['.venv/bin/python', "-m", "pip", "install", package])    # nosec
    # f = open('requirements.txt', 'w')
    # f.write(os.popen(soil_root + '/.venv/bin/pip freeze').read())    # nosec
    # f.close()


def run(args: argparse.Namespace) -> None:
    """
    Runs the script provided as argument using the python in the virtual environment
    """

    soil_root = get_soil_root(".")
    if not soil_root:
        print(
            "This folder is not initalized as a soil project. Please run soil init to initialize it."
        )
        sys.exit()

    chapter = vars(args)["chapter"]
    module = vars(args)["module"]
    module_args = vars(args)["module_args"]

    os.chdir(soil_root)
    with open("soil.yml") as f:
        conf = yaml.safe_load(f)
    try:
        script = [script for script in conf[chapter] if script.get(module) is not None][
            0
        ][module]
    except (IndexError, KeyError):
        print("Script", module, "not found.")
        sys.exit()
    params = script.get("params", {})
    params = [["--" + k, str(v)] for (k, v) in params.items()]
    params = [item for sublist in params for item in sublist]
    try:
        shell = [".venv/bin/python", "-m", script["path"]] + module_args + params
        print("Running:", " ".join(shell))
        subprocess.run(shell, check=True)  # nosec
    except subprocess.CalledProcessError:
        sys.exit()


def test(args: argparse.Namespace) -> None:
    """
    Launches tests in the test folder.
    """
    soil_root = get_soil_root(".")
    if not soil_root:
        print(
            "This folder is not initalized as a soil project. Please run soil init to initialize it."
        )
        sys.exit()

    test_args = vars(args)["test_args"]

    os.chdir(soil_root)
    try:
        subprocess.run([".venv/bin/python", "-m", "unittest"] + test_args, check=True)  # nosec

    except subprocess.CalledProcessError:
        sys.exit()


def main() -> None:
    """main function"""

    args = parser.parse_args()

    config, env = soil_init()

    try:
        if args.command == "configure":
            configure(args, config)
        elif args.command == "login":
            login(args, config, env)
        elif args.command == "init":
            init(args)
        elif args.command == "install":
            install(args)
        elif args.command == "run":
            run(args)
        elif args.command == "test":
            test(args)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt - Exit...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)  # NOQA # pylint: disable=protected-access


if __name__ == "__main__":
    main()
