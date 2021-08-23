#!/usr/bin/env python3
import argparse
import logging
import os
from os import path as op
import shutil

import jaad

BIN_DIR = op.dirname(op.abspath(__file__))
JAAD_DIR = op.dirname(jaad.__file__)
TEMPLATE_FOLDER = op.join(JAAD_DIR, "templates")
PROJECT_DIR = os.getcwd()


def run_commands(commands, force):
    for command in commands:
        run_command(command, force)


def run_command(command, force):
    if command == "startproject":
        copy_from_template("startproject", force)
    elif command == "add-doc":
        copy_from_template("add-doc", force)
        # todo:
        print("Add `url(r'^doc/', include('documentation.urls'))` to your url pattern")
        # todo:
        print(
            "And `'server.apps.documentation'` to your INSTALLED_APPS in application settings"
        )
        # todo:
        print("Run django-admin collectstatic")
    elif command == "add-uwsgi":
        copy_from_template("add-uwsgi", force)
    else:
        raise ValueError(f"Unrecognized command {command}")


def copy_from_template(template_name, force, dry_run=False):
    if dry_run is False:
        # Whenever a copy is tried, first apply a dry run
        copy_from_template(template_name, force, dry_run=True)
    command_template_dir = op.join(TEMPLATE_FOLDER, template_name)
    for path, directories, files in os.walk(command_template_dir):
        rel_path = path[len(command_template_dir) + 1 :]
        for directory in directories:
            destination = op.join(PROJECT_DIR, rel_path, directory)
            if os.path.exists(destination):
                continue
            logging.debug(f"Creating directory {destination!r}")
            if not dry_run:
                os.mkdir(destination)
        for file in files:
            origin = op.join(command_template_dir, rel_path, file)
            destination = op.join(PROJECT_DIR, rel_path, file)
            logging.debug(f"Copying from {origin!r} {destination!r}")
            if not os.path.exists(origin):
                raise Exception(
                    f"An unexpected error occured as the origin template file does not exist: {origin}"
                )
            if not force and os.path.exists(destination):
                raise Exception(
                    "A file that would have been generated already exists: "
                    f"{destination}. "
                    "Check the command or use --force to force the execution"
                )
            if not dry_run:
                shutil.copyfile(origin, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "commands", choices=["startproject", "add-doc", "add-uwsgi"], nargs="+"
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    run_commands(args.commands, args.force)
    return 0


if __name__ == "__main__":
    exit(main())
