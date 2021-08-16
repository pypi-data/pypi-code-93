import logging
import sys
import webview  # type: ignore
from inspector.context import Context
from inspector.metric import MetricStart

PYWEBVIEW_GUI = ["qt", "gtk", "cef", "mshtml", "edgechromium", "edgehtml"]


class App:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.ctx = Context(self.logger, config)

    def start(self, root="manager"):
        assert not self.ctx.windows, "Application already running"

        self.ctx.database.load()
        if self.ctx.database.error:
            self.logger.warning(*self.ctx.database.error)

        root = self.ctx.open_window(root)
        root.closed += self.stop

        self.ctx.telemetry.send(MetricStart())
        webview.start(self._on_start, debug=self.ctx.is_debug)

    def stop(self):
        self.ctx.close_windows()

    def add(self, kind):
        self.start(kind)

    def edit(self, name):
        locator = self.ctx.load_locator(name)

        if locator is None:
            names = "\n".join(f" - {name}" for name in self.ctx.database.names)
            if names:
                print(f"No locator with name: {name}\n")
                print(f"Possible options:\n{names}")
            else:
                print("No locators in database")
            sys.exit(1)

        self.ctx.selected = name
        self.start(locator["type"])

    def _on_start(self):
        self.logger.info("Starting root window")
        if self.ctx.is_debug:
            # Print URL for automation
            root = self.ctx.windows[0]
            self.logger.info(root.get_current_url())
