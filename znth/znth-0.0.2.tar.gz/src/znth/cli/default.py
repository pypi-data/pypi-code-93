import logging
import readline

from znth.factory.default import DefaultFactory


class DefaultProcessor(object):
    def __init__(self, level = logging.ERROR):
        self.log_level = level

        # Setup GNU Readline support


    def input(self, prompt: str, value: str = "") -> str:
        readline.set_startup_hook(lambda: readline.insert_text(value))

        try:
            line = input(prompt)
        finally:
            readline.set_startup_hook()

        return line