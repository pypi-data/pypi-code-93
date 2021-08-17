from pathlib import Path
from typing import Callable
from copy import copy

def is_file_setup_file(file: Path):
    return str(file.name) == "setup.py" or str(file.name) == "setup.cfg"


class CouldNotLocateRepositoryDirException(Exception):
    def __init__(self, repo_dir_detection_fn: Callable[[Path], bool], start_dir: Path):
        err_msg = f"Could not locate a repository directory in the dir and super dirs \
             of {str(start_dir.resolve())} via {repo_dir_detection_fn.__name__}"
        return super().__init__(err_msg)


class RepositoryDirLocator:

    def __init__(self, start_dir: Path = Path(__file__).parent) -> None:
        """

        Args:
            start_dir ([Path], optional): [The path to the direcory from which to start the search for the repository dir in parent dirs]. Defaults to Path(__file__).parent.
        """
        self.start_dir = start_dir
        self._repo_dir = self.locate_repo_dir()
        

    @property
    def repo_dir(self) -> Path:
        return self._repo_dir



    def locate_repo_dir(self, repo_dir_detection_fn: Callable[[Path], bool] = is_file_setup_file) -> Path:
        """A function that locates the repository directory given a predicate function as defined below

        Args:
            repo_dir_detection_fn (Callable[[Path], bool]): [A predicate function of a file in the repository directory, i.e.
            if a directory is the repository directory it must return true for at least one of its files]
        """

        current_dir: Path = copy(self.start_dir)
        repo_dir = None

        def _locate_dir(current_dir):
            for file in current_dir.iterdir():
                if(repo_dir_detection_fn(file)):
                    return current_dir


        while(repo_dir is None):
            repo_dir = _locate_dir(current_dir)
            if (current_dir.parent is current_dir):
                raise CouldNotLocateRepositoryDirException(repo_dir_detection_fn, self.start_dir)
            else:
                current_dir = current_dir.parent
        
        return repo_dir
