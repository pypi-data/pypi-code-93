from pathlib import Path
from typing import List

from flake8.api import legacy
from flake8.formatting.base import BaseFormatter
from flake8.main.application import Application
from flake8.options import config as flake_config
from flake8.style_guide import Violation

from .base import Linter
from ..config import Config


class Formatter(BaseFormatter):
    errors: List[str] = None

    def after_init(self):
        Formatter.errors = []

    def format(self, error: Violation) -> str:
        return (
            f"{error.filename}:{error.line_number}:{error.column_number}"
            f": {error.code} {error.text}"
        )

    def write(self, line: str, source: str):
        Formatter.errors.append(line)


class Flake8Linter(Linter):
    def __init__(self, config: Config) -> None:
        super().__init__(config)

        self.app = Application()
        args = [
            "--isolated",
            "--max-line-length",
            str(config.line_length),
            "--import-order-style",
            "pep8",
            "--ignore",
            "E203,W503",
        ]
        if config.exclude:
            args.extend(["--extend-exclude", config.exclude])
        if config.application_import_names:
            args.extend(["--application-import-names", config.application_import_names])

        prelim_opts, remaining_args = self.app.parse_preliminary_options(args)

        config_finder = flake_config.ConfigFileFinder(
            self.app.program,
            prelim_opts.append_config,
            config_file=prelim_opts.config,
            ignore_config_files=prelim_opts.isolated,
        )
        self.app.find_plugins(config_finder)
        self.app.register_plugin_options()
        self.app.parse_configuration_and_cli(config_finder, remaining_args)
        self.app.make_formatter()
        self.app.make_guide()
        self.app.make_file_checker_manager()

    def run(self, paths: List[Path]) -> List[str]:
        style_guide = legacy.StyleGuide(self.app)
        style_guide.init_report(Formatter)
        style_guide.check_files(paths)
        return Formatter.errors

    def dump_config(self, dst: Path) -> None:
        with open(dst / ".flake8", "w") as out:
            out.write("[flake8]\n")
            out.write(f"max-line-length = {self.app.options.max_line_length}\n")
            out.write(f"import-order-style = {self.app.options.import_order_style}\n")
            out.write(f'ignore = {",".join(self.app.options.ignore)}\n')
            if self.app.options.extend_exclude:
                out.write(
                    f'extra-exclude = {",".join(self.app.options.extend_exclude)}\n'
                )
            if self.app.options.application_import_names:
                out.write(
                    "application-import-names = "
                    f'{",".join(self.app.options.application_import_names)}\n'
                )

    @property
    def name(self):
        return "flake8"
