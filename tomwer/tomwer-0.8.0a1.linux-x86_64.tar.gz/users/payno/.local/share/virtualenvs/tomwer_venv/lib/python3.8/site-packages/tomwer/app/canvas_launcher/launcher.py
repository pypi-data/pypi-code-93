import os
import sys

from silx.gui import qt
from orangecanvas import config, __main__ as main

# from Orange.canvas import config, __main__ as main
# from Orange.misc import environ
from .splash import splash_screen, getIcon
import tomwer.version
from tomwer.gui import icons
from tomwer.core.log.logger import _formatter_message, _ColoredFormatter
from tomwer.web.config import grayport_host, grayport_port
from urllib.request import urlopen
import logging

try:
    import graypy

    has_graypy = True
except:
    has_graypy = False

_logger = logging.getLogger(__name__)


def version():
    return tomwer.version.version


class TomwerConfig(config.Config):
    ApplicationName = "tomwer"
    ApplicationVersion = version()

    @staticmethod
    def splash_screen():
        return splash_screen()

    @staticmethod
    def core_packages():
        return super(TomwerConfig, TomwerConfig).core_packages() + ["tomwer-add-on"]

    @staticmethod
    def application_icon():
        return getIcon()


class TomwerSplashScreen(qt.QSplashScreen):
    def __init__(
        self,
        parent=None,
        pixmap=None,
        textRect=None,
        textFormat=qt.Qt.PlainText,
        **kwargs
    ):
        super(TomwerSplashScreen, self).__init__(pixmap=icons.getQPixmap("tomwer"))

    def showMessage(self, message, alignment=qt.Qt.AlignLeft, color=qt.Qt.black):
        version = "tomwer version {}".format(tomwer.version.version)
        super().showMessage(version, qt.Qt.AlignLeft | qt.Qt.AlignBottom, qt.Qt.white)


class Launcher:
    """Proxy to orange-canvas"""

    def launch(self, argv):
        config.Config = TomwerConfig
        self.fix_application_dirs()
        self.replace_splash_screen()
        self.main(argv)

    def fix_application_dirs(self):
        def data_dir(versioned=True):
            """
            Return the platform dependent Orange data directory.

            This is ``data_dir_base()``/Orange/__VERSION__/ directory if versioned is
            `True` and ``data_dir_base()``/Orange/ otherwise.
            """
            # base = environ.data_dir_base()
            # if versioned:
            #     return os.path.join(base, "tomwer", version())
            # else:
            #     return os.path.join(base, "tomwer")

        # environ.data_dir = data_dir

        def cache_dir(*args):
            """
            Return the platform dependent Orange cache directory.
            """
            if sys.platform == "darwin":
                base = os.path.expanduser("~/Library/Caches")
            elif sys.platform == "win32":
                base = os.getenv("APPDATA", os.path.expanduser("~/AppData/Local"))
            elif os.name == "posix":
                base = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
            else:
                base = os.path.expanduser("~/.cache")

            base = os.path.join(base, "tomwer", version())
            if sys.platform == "win32":
                # On Windows cache and data dir are the same.
                # Microsoft suggest using a Cache subdirectory
                return os.path.join(base, "Cache")
            else:
                return base

        # environ.cache_dir = cache_dir

    def replace_splash_screen(self):
        main.SplashScreen = TomwerSplashScreen

    def graylog_dau_is_available(self):
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((grayport_host, grayport_port))
            s.shutdown(2)
            return True
        except:
            return False

    def add_graypy_handler(self, my_logger):
        if not self.graylog_dau_is_available():
            return

        if os.environ.get("ORANGE_WEB_LOG", "True") == "True":
            if hasattr(graypy, "GELFHandler"):
                constructor = graypy.GELFHandler
            elif hasattr(graypy, "GELFUDPHandler"):
                constructor = graypy.GELFUDPHandler
            else:
                _logger.warning("Fail to find the correct constructor from graypy")
                return

            try:
                self.graylogHandler = constructor(grayport_host, grayport_port)
            except:
                _logger.warning("Fail to create GELFHandler. Won't report log message")
            else:
                my_logger.addHandler(self.graylogHandler)
                _logger.debug("- add graypy handler")
        else:
            info = "No log will be send to graylog."
            info += "ORANGE_WEB_LOG variable is setted to False"
            _logger.debug(info)

    def main(self, argv):
        from Orange.canvas.__main__ import main

        # from Orange.canvas.__main__ import main
        import optparse

        if argv is None:
            argv = sys.argv

        usage = "usage: %prog [options] [workflow_file]"
        parser = optparse.OptionParser(usage=usage)

        parser.add_option(
            "--no-discovery",
            action="store_true",
            help="Don't run widget discovery " "(use full cache instead)",
        )
        parser.add_option(
            "--force-discovery",
            action="store_true",
            help="Force full widget discovery " "(invalidate cache)",
        )
        parser.add_option(
            "--load-widget-settings",
            dest="clear_widget_settings",
            action="store_false",
            default=True,
            help="Load widget setting stored",
        )
        parser.add_option(
            "--no-welcome", action="store_true", help="Don't show welcome dialog."
        )
        parser.add_option(
            "--no-splash", action="store_true", help="Don't show splash screen."
        )
        parser.add_option(
            "-l",
            "--log-level",
            help="Logging level (0, 1, 2, 3, 4)",
            type="int",
            default=1,
        )
        parser.add_option("--style", help="QStyle to use", type="str", default=None)
        parser.add_option(
            "--stylesheet",
            help="Application level CSS style sheet to use",
            type="str",
            default=None,
        )
        parser.add_option(
            "--qt",
            help="Additional arguments for QApplication",
            type="str",
            default=None,
        )
        parser.add_option(
            "--all-addon",
            action="store_true",
            help="display only add-on widgets",
            default=False,
        )
        parser.add_option(
            "--no-color-stdout-logs",
            "--no-colored-logs",
            action="store_true",
            help="instead of having logs in the log view, color logs of the stdout",
            default=False,
        )
        (options, args) = parser.parse_args(argv[1:])
        levels = [
            logging.CRITICAL,
            logging.ERROR,
            logging.WARN,
            logging.INFO,
            logging.DEBUG,
        ]
        log_level = min(levels[options.log_level], logging.WARNING)
        for logger_name in (
            "fabio",
            "tomoscan",
            "nxtomomill",
            "tomwer",
            "nxtomomill.converter",
            "orangecontrib",
            "silx",
        ):
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)

        # update tomwer logger
        FORMAT = (
            "%(asctime)s [%(levelname)-18s] %(message)s [$BOLD%(name)-20s$RESET]"
            "($BOLD%(filename)s$RESET:%(lineno)d)"
        )
        self.color_format = _formatter_message(
            FORMAT,
            use_color=os.environ.get("ORANGE_COLOR_STDOUT_LOG", "False") == "True",
        )

        color_formatter = _ColoredFormatter(self.color_format)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        tomwer_logger = logging.getLogger("tomwer")

        if has_graypy:
            self.add_graypy_handler(tomwer_logger)
        else:
            logger.info("graypy not install. No log will be send to graylog")

        if check_is_latest_release():
            main(argv)


def check_is_latest_release() -> bool:
    """Check if the current version is the latest release."""
    url = "https://gitlab.esrf.fr/tomotools/tomwer/-/raw/master/tomwer/version.py"
    current_version = tomwer.version.version
    try:
        version_file_html = urlopen(url, data=None, timeout=10)
    except Exception as e:
        _logger.warning(
            "Fail to load version of the latest release." " Reason is {}".format(e)
        )
        return True
    else:
        latest_release_version = None
        for line in version_file_html.readlines():
            t_line = line.decode("utf-8")
            t_line = t_line.replace(" ", "")
            if t_line.startswith("latest_release_version_info="):
                latest_release_version = t_line.replace(
                    "latest_release_version_info=", ""
                )
                break
        if latest_release_version is None:
            _logger.warning("Unable to find the version of the latest " "release.")

        elif current_version < latest_release_version:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Question)
            types = qt.QMessageBox.Ok | qt.QMessageBox.Cancel
            message = (
                "The version you want to use ({}) is not the latest "
                "version ({}). Do you want to continue ?"
            )
            msg.setStandardButtons(types)
            msg.setWindowTitle("No the latest version")
            msg.setText(message)
            return msg.exec_() == qt.QMessageBox.Ok
        return True
