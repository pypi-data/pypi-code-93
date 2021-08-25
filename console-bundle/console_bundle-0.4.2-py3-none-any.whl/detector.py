import sys
import shutil
from pathlib import Path
from consolebundle import CommandRunner


def is_running_in_console():
    def compare_executables(p1: Path, p2: Path):
        return p1.parents[0] == p2.parents[0] and p1.stem == p2.stem

    invoked_using_command_runner = Path(sys.argv[0]) == Path(CommandRunner.__file__)

    console_path = shutil.which("console")
    invoked_using_script = console_path is not None and compare_executables(Path(sys.argv[0]), Path(console_path))

    return invoked_using_command_runner or invoked_using_script
