import datetime
import getpass
import logging
import logging.handlers
import os
import pathlib
import readline
import sys

from znth.chain import Command, CommandState, Context, ContextKeyException


class ZenithCommand(Command):
    """
    InitializeCommand: Sets defaults in the context.
    """

    def execute(self, context: Context) -> bool:
        if "zenith_dir" not in context:
            current_dir = os.getcwd()
            zenith_dir = None

            while zenith_dir is None:
                tmp = os.path.join(current_dir, '.zenith')

                if os.path.isdir(tmp):
                    zenith_dir = tmp
                else:
                    if current_dir == pathlib.Path(current_dir).parent:
                        break
                    else:
                        current_dir = pathlib.Path(current_dir).parent

            if zenith_dir:
                context["zenith_dir"] = zenith_dir

        zenith_dir = context["zenith_dir"]
        context["db_dir"] = os.path.join(zenith_dir, "var", "db")
        context["db_filename"] = os.path.join(zenith_dir, "var", "db", "zenith.db")
        context["etc_dir"] = os.path.join(zenith_dir, "var", "etc")
        context["log_dir"] = os.path.join(zenith_dir, "var", "log")
        context["tmp_dir"] = os.path.join(zenith_dir, "var", "tmp")

        return Command.SUCCESS


class ZenithDirectoryCommand(Command):
    """
    ProcessingCommand: Creates Zenith directories.
    """

    def execute(self, context: Context) -> bool:
        if "zenith_dir" not in context:
            raise ContextKeyException("zenith_dir")

        if "db_dir" not in context:
            raise ContextKeyException("db_dir")

        if "log_dir" not in context:
            raise ContextKeyException("log_dir")

        if "tmp_dir" not in context:
            raise ContextKeyException("tmp_dir")

        if not os.path.isdir(context["db_dir"]):
            os.makedirs(context["db_dir"])
        if not os.path.isdir(context["log_dir"]):
            os.makedirs(context["log_dir"])
        if not os.path.isdir(context["tmp_dir"]):
            os.makedirs(context["tmp_dir"])

        return Command.SUCCESS


class LoggingCommand(Command):
    """
    InitializingCommand: Initializes logging.
    """

    def __init__(self, level = logging.ERROR):
        super().__init__()
        self.level = level
        self.log_dir = ""
        self.app_name = ""

    def daily_log_filename(self):
        now = datetime.datetime.now()
        name = f"{self.app_name}-{now.strftime('%Y%m%d')}.log"
        filename = os.path.join(self.log_dir, name)
        return filename

    def execute(self, context: Context) -> bool:
        if "log_dir" not in context:
            raise ContextKeyException("log_dir")

        self.log_dir = context["log_dir"]

        if "app_name" in context:
            self.app_name = context["app_name"]
        else:
            self.app_name = "zenith"

        if "logfile" in context:
            logfile = context["logfile"]
        else:
            logfile = True

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        format0 = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        console = logging.StreamHandler()
        console.setFormatter(format0)
        root.addHandler(console)

        if sys.stdout.isatty():
            console.setLevel(self.level)
        else:
            console.setLevel(logging.FATAL)

        if logfile:
            format1 = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(levelname)s - %(message)s',
                                        datefmt='%Y-%m-%d %H:%M:%S')
            fh = logging.handlers.TimedRotatingFileHandler(filename=self.daily_log_filename(), when="d")
            fh.rotation_filename = self.daily_log_filename
            fh.setFormatter(format1)
            if self.level == logging.DEBUG:
                fh.setLevel(logging.DEBUG)
            else:
                fh.setLevel(logging.INFO)
            root.addHandler(fh)

        return Command.SUCCESS


class ReportCommand(Command):
    """
    ReportingCommand: Reports result.
    """

    def __init__(self):
        self.start = datetime.datetime.now()
        self.app_name = ""

    def execute(self, context: Context) -> bool:
        logger = logging.getLogger(__name__)

        if "app_name" in context:
            self.app_name = context["app_name"]
        else:
            self.app_name = "zenith"

        logger.info(f"{self.app_name} - Start")

        return Command.SUCCESS

    def post_execute(self, context: Context, state: CommandState, error: Exception = None) -> None:
        logger = logging.getLogger(__name__)
        delta = datetime.datetime.now() - self.start
        duration_ms = delta.total_seconds() * 1000.0

        if "user" in context:
            user = context["user"]
        else:
            user = "<Unknown>"

        if state == CommandState.ERROR:
            status = "Error"
        elif state == CommandState.FAILURE:
            status = "Failure"
        elif state == CommandState.SUCCESS:
            status = "Success"
        else:
            status = "Unknown"

        logger.info(f"{self.app_name} - Finish: {user} - {status} ({duration_ms:0.3f} ms)")


class AuthenticationCommand(Command):
    """
    AuthenticationCommand: Logs username.
    """

    def execute(self, context: Context) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("authenticate.execute() - Start")

        context["user"] = getpass.getuser()

        logger.debug("authenticate.execute() - Finish")
        return Command.SUCCESS


class ReadlineCommand(Command):
    """
    ReadlineCommand: Setups GNU Readline.
    """
    def execute(self, context: Context) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("readline.execute() - Start")

        if "etc_dir" not in context:
            raise ContextKeyException("etc_dir")

        etc_dir = context["etc_dir"]

        if not os.path.isdir(etc_dir):
            os.makedirs(etc_dir)

        self.history_filename = os.path.join(etc_dir, "zenith_history")

        try:
            readline.parse_and_bind('tab: complete')
            readline.parse_and_bind('set editing-mode vi')
            readline.read_history_file(self.history_filename)
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass

        logger.debug("readline.execute() - Finish")
        return Command.SUCCESS

    def post_execute(self, context: Context, state: CommandState, error: Exception = None) -> None:
        logger = logging.getLogger(__name__)
        logger.debug("readline.post_execute() - Start")

        if state != CommandState.ERROR:
            readline.set_history_length(1000)
            readline.write_history_file(self.history_filename)

        logger.debug("readline.post_execute() - Finish")
