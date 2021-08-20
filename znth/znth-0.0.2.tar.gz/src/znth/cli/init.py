import os
import pathlib

from znth.cli.default import DefaultProcessor
from znth.command.database import DatabaseContext
from znth.factory.init import InitFactory


class InitProcessor(DefaultProcessor):
    def init(self, direcory: str) -> None:
        if not direcory:
            zenith_dir = os.path.join(pathlib.Path(os.getcwd()).absolute(), ".zenith")
        elif ".zenith" == pathlib.Path(direcory).name:
            zenith_dir = pathlib.Path(direcory).absolute()
        else:
            zenith_dir = os.path.join(pathlib.Path(direcory).absolute(), ".zenith")

        context = DatabaseContext()
        context["zenith_dir"] = zenith_dir
        context["logfile"] = False

        runner = InitFactory.create_init(self.log_level)
        runner.execute(context)
