import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Union, TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from pbt.package import Package


class Poetry:
    @classmethod
    def get_python_file(cls, package_dir: Union[str, Path]):
        if sys.prefix != sys.base_prefix:
            logger.error(
                "Can't obtain the python executable file because the virtual environment is active."
            )
            raise Exception(
                "Can't obtain the python executable file because the virtual environment is active."
            )

        pres = subprocess.run(
            ["poetry", "env", "info", "-p"],
            cwd=str(package_dir),
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
        )
        python_file = pres.stdout.decode().strip()
        assert "\n" not in python_file
        python_file = Path(python_file) / "bin/python"
        assert python_file.exists()
        return python_file

    @classmethod
    def get_pip_file(cls, package_dir: Union[str, Path]):
        return Poetry.get_python_file(package_dir).parent / "pip"

    @classmethod
    def update_package(
        cls, target_package: "Package", package_name: str, package_version: str
    ):
        should_update = False
        with open(os.path.join(target_package.dir, "pyproject.toml"), "r") as f:
            lines = f.readlines()
            match_lines = [
                (i, line)
                for i, line in enumerate(lines)
                if re.match(f"{package_name} *= *", line) is not None
            ]
            assert len(match_lines) == 1
            idx, line = match_lines[0]
            m = re.match(
                rf"""({package_name} *= *)(?:'|")([^0-9]*)([^'"]+)(?:'|")(.*)""", line,
                flags=re.DOTALL
            )
            if m is not None:
                groups = m.groups()
                prev_version = groups[2]
                if prev_version != package_version:
                    should_update = True
                    logger.info(
                        f"In {target_package.name}, bump {package_name} from `{prev_version}` to `{package_version}`"
                    )
                    lines[idx] = f'{groups[0]}"{groups[1]}{package_version}"{groups[3]}'
            else:
                raise NotImplementedError(f"Do not know how to parse `{line}` yet")

        if should_update:
            with open(os.path.join(target_package.dir, "pyproject.toml"), "w") as f:
                for line in lines:
                    f.write(line)
