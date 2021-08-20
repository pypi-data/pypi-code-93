import argparse
import logging

from znth.cli.init import InitProcessor
from znth.cli.client import ClientProcessor
from znth.cli.task import TaskProcessor
from znth.cli.project import ProjectProcessor

def main():
    parser = argparse.ArgumentParser(prog="zenith")
    parser.add_argument("-d", "--debug", dest="debug", default=False, action="store_true", help="Print debug information")
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true", help="Print verbose information")

    subparser = parser.add_subparsers(dest="process")

    init = subparser.add_parser("init", help="Initialize Zenith")
    init.add_argument("dir", nargs="?", help="Directory, default current directory")

    client = subparser.add_parser("client", help="Client commands")
    client_subparser = client.add_subparsers(dest="command")
    client_activate = client_subparser.add_parser("activate", help="Activates a client")
    client_activate.add_argument("name", help="Name of the client")
    client_create = client_subparser.add_parser("create", help="Creates a client")
    client_create.add_argument("name", help="Name of the client")
    client_read = client_subparser.add_parser("read", help="Reads a client")
    client_read.add_argument("name", help="Name of the client")
    client_update = client_subparser.add_parser("update", help="Updates a client")
    client_update.add_argument("name", help="Name of the client")
    client_delete = client_subparser.add_parser("delete", help="Deletes a client")
    client_delete.add_argument("name", help="Name of the client")
    client_list = client_subparser.add_parser("list", help="Lists all clients")

    project = subparser.add_parser("project", help="Project commands")
    project_subparser = project.add_subparsers(dest="command")
    project_activate = project_subparser.add_parser("activate", help="Activates a project")
    project_activate.add_argument("name", help="Name of the project")
    project_create = project_subparser.add_parser("create", help="Creates a project")
    project_create.add_argument("name", help="Name of the project")
    project_read = project_subparser.add_parser("read", help="Reads a project")
    project_read.add_argument("name", help="Name of the project")
    project_update = project_subparser.add_parser("update", help="Updates a project")
    project_update.add_argument("name", help="Name of the project")
    project_delete = project_subparser.add_parser("delete", help="Deletes a project")
    project_delete.add_argument("name", help="Name of the project")
    project_list = project_subparser.add_parser("list", help="Lists all projects")

    task = subparser.add_parser("task", help="Task commands")
    task_subparser = task.add_subparsers(dest="command")
    task_new = task_subparser.add_parser("new", help="Creates a new task")
    task_start = task_subparser.add_parser("start", help="Starts the task")
    task_start.add_argument("id", type=int, help="ID of the task")
    task_stop = task_subparser.add_parser("stop", help="Stops the task")
    task_stop.add_argument("id", type=int, help="ID of the task")
    task_read = task_subparser.add_parser("read", help="Reads the task")
    task_read.add_argument("id", type=int, help="ID of the task")
    task_update = task_subparser.add_parser("update", help="Updates the task")
    task_update.add_argument("id", type=int, help="ID of the task")
    task_delete = task_subparser.add_parser("delete", help="Deletes the task")
    task_delete.add_argument("id", type=int, help="ID of the task")
    task_list = task_subparser.add_parser("list", help="Lists all tasks")

    args = parser.parse_args()

    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    else:
        level = logging.ERROR

    if "init" == args.process:
        processor = InitProcessor(level)
        processor.init(args.dir)
    elif "client" == args.process:
        processor = ClientProcessor(level)

        if args.command == "activate":
            processor.activate(args.name)
        elif args.command == "create":
            processor.create(args.name)
        elif args.command == "read":
            processor.read(args.name)
        elif args.command == "update":
            processor.update(args.name)
        elif args.command == "delete":
            processor.delete(args.name)
        elif args.command == "list":
            processor.list()
        else:
            client.print_help()
    elif "project" == args.process:
        processor = ProjectProcessor(level)

        if args.command == "activate":
            processor.activate(args.name)
        elif args.command == "create":
            processor.create(args.name)
        elif args.command == "read":
            processor.read(args.name)
        elif args.command == "update":
            processor.update(args.name)
        elif args.command == "delete":
            processor.delete(args.name)
        elif args.command == "list":
            processor.list()
        else:
            project.print_help()
    elif "task" == args.process:
        processor = TaskProcessor(level)

        if args.command == "new":
            processor.new()
        elif args.command == "start":
            processor.start(args.id)
        elif args.command == "stop":
            processor.stop(args.id)
        elif args.command == "read":
            processor.read(args.id)
        elif args.command == "update":
            processor.update(args.id)
        elif args.command == "delete":
            processor.delete(args.id)
        elif args.command == "list":
            processor.list()
        else:
            task.print_help()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()