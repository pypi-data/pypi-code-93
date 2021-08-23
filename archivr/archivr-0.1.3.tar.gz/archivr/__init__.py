import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List

from tqdm import tqdm


@contextmanager
def working_dir(dir: Path) -> Generator[Path, None, None]:
    try:
        cwd = os.curdir
        os.chdir(dir)
        yield dir
    finally:
        os.chdir(cwd)


def get_folders(src: Path) -> List[Path]:
    """Gets all subfolders of the given path."""

    return [x for x in src.iterdir() if x.is_dir()]


def get_files(src: Path) -> List[Path]:
    """Gets all files in the given directory."""

    return [x for x in src.iterdir() if x.is_file()]


def clean(path: Path) -> None:
    """Removes all contents of the given path."""
    for f in path.iterdir():
        if f.is_dir():
            clean(f)
            f.rmdir()
            continue

        f.unlink()


def archive(dir: str) -> None:
    """Zips all folders in `src` and saves them to an `archive` folder."""
    src: Path = Path(dir)
    with working_dir(src) as d:
        archive = d / "arch"
        archive.mkdir()
        folders = get_folders(d)
        folders.remove(archive)
        for folder in tqdm(folders):
            archive_name = Path(f"arch/{folder.name}").resolve()
            shutil.make_archive(str(archive_name), "zip", folder)

        for file in get_files(d):
            shutil.copyfile(file, archive / file)
