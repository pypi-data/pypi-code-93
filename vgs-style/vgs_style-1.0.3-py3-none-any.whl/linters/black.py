from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import black

from .base import Linter
from ..config import Config


class BlackLinter(Linter):
    def __init__(self, config: Config) -> None:
        self.config = {
            "line_length": config.line_length,
        }
        if config.exclude:
            self.config["exclude"] = "|".join(
                expr.replace(".", r"\.").replace("*", ".*") for expr in config.exclude
            )

    def dump_config(self, dst: Path) -> None:
        with open(dst / "black.toml", "w") as out:
            out.write("[tool.black]\n")
            out.write(f'line_length = {self.config["line_length"]}\n')
            if "exclude" in self.config:
                out.write(f'exclude = "{self.config["exclude"]}"\n')

    def run(self, paths: List[Path]) -> List[str]:
        return self._run(paths, check=True)

    def format(self, paths: List[Path]) -> None:
        self._run(paths, check=False)

    @property
    def name(self):
        return "black"

    def _run(self, paths: List[Path], check: bool) -> List[str]:
        # Hardcoded params
        quiet = True
        verbose = False
        force_exclude = None
        fast = True
        diff = False
        color = False
        include = black.DEFAULT_INCLUDES

        write_back = black.WriteBack.from_configuration(
            check=check, diff=diff, color=color
        )
        versions = set()
        mode = black.Mode(
            target_versions=versions,
            line_length=self.config["line_length"],
            is_pyi=False,
            experimental_string_processing=False,
        )
        report = Report(check=check)

        sources = black.get_sources(
            ctx=None,  # TODO: emulate click context
            src=tuple(paths),
            quiet=quiet,
            verbose=verbose,
            include=include,
            exclude=self.config.get("exclude", black.DEFAULT_EXCLUDES),
            force_exclude=force_exclude,
            report=report,
        )

        if not sources:
            return []

        if len(sources) == 1:
            black.reformat_one(
                src=sources.pop(),
                fast=fast,
                write_back=write_back,
                mode=mode,
                report=report,
            )
        else:
            black.reformat_many(
                sources=sources,
                fast=fast,
                write_back=write_back,
                mode=mode,
                report=report,
            )

        return report.errors


@dataclass
class Report(black.Report):
    errors: List[str] = field(default_factory=list)

    def done(self, src: Path, changed: black.Changed) -> None:
        if changed is black.Changed.YES and self.check:
            self.errors.append(f"{src}: would reformat")
            self.change_count += 1

    def failed(self, src: Path, message: str) -> None:
        self.errors.append(f"{src}: cannot format")
        self.failure_count += 1
