"""Task specification."""
import subprocess  # nosec
from pathlib import Path
from typing import List, Optional


class Task:
    """Class representing a linter or spell checker task."""

    # pylint: disable=too-few-public-methods

    title: str
    _command: str
    _glob_file_type: Optional[str]
    _args: List[str]

    def __init__(
        self,
        title: str,
        command: str,
        args: List[str] = None,
        glob_file_type: Optional[str] = None,
    ):
        """
        Initialize a new task specification.

        Args:
            title (str): Title of the task for showing in CLI
            command (str): name of command to run.
            args (List[str], optional): CLI arguments. Should not include arguments
                specifying what files to process. Defaults to None.
            glob_file_type (Optional[str], optional): The base folder will be searched
                for files of this type and they will be added as arguments. Defaults to
                None.

        """
        self.title = title
        self._command = command
        self._glob_file_type = glob_file_type
        self._args = args or []

        if glob_file_type is not None and glob_file_type not in ["py", "md"]:
            raise Exception("Bad file type", glob_file_type)

    def run(self) -> int:
        """
        Run the task.

        Returns:
            int: The return code of the task. Can be use to check whether the task
            passed or failed.
        """
        print(f"🐍 {self.title}{' ' * (30-len(self.title))}", end="", flush=True)
        files = self._list_files()
        process = subprocess.run(  # nosec
            [self._command, *self._args, *files],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        if process.returncode == 0:
            print("✅")
            return process.returncode

        print("🚫")
        if process.stdout:
            print(process.stdout.strip())
        if process.stderr:
            print(process.stderr.strip())
        print("")
        return process.returncode

    def _list_files(self, base_folder: Path = None) -> List[str]:
        if not self._glob_file_type:
            return []

        if base_folder is None:
            base_folder = Path(".")
        temp = []
        for path in base_folder.glob(f"**/*.{self._glob_file_type}"):
            if any(part[0] == "." for part in path.parts):
                continue
            if path.parts[0] == "build":
                continue
            path = str(path.relative_to(base_folder))
            temp.append(path)
        return temp
