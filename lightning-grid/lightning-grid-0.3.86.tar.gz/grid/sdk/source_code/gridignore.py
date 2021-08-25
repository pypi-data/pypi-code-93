"""TODO(rlizzo): THIS FILE IS PART OF PROJECT FEYNMAN
"""
from pathlib import Path
from typing import Set


def generate(src: Path) -> Set[str]:
    """
    Generates list of glob strings to ignore. These need to be parsed to identify
    which files are actually ignored.

    Returns
    -------
    Set[str]
        Glob strings to parse
    """
    # fallback files in case we can't find .gridignore
    fallback_ignore_files = {".dockerignore", ".gitignore"}

    # never include these paths in the package
    excluded_paths = {".git"}

    # if it is a file, then just read from it and return lines
    if src.is_file():
        return _read_and_filter(src)

    # ignores all paths from excluded paths by default
    ignore_globs = {f"{p}/" for p in excluded_paths}

    # look first for `.gridignore` files
    for path in src.glob('**/*'):
        if path.name in excluded_paths:
            continue
        if path.is_file():
            if path.name == ".gridignore":
                filtered = _read_and_filter(path)
                relative_dir = path.relative_to(src).parents[0]
                relative_globs = [str(relative_dir / glob) for glob in filtered]
                ignore_globs.update(relative_globs)

    # if found .gitignore, return it
    if len(ignore_globs) > len(excluded_paths):
        return ignore_globs

    # if not found, look everything else
    for path in src.glob('**/*'):
        if path.name in excluded_paths:
            continue
        if path.is_file():
            if path.name in fallback_ignore_files:
                filtered = _read_and_filter(path)
                relative_dir = path.relative_to(src).parents[0]
                relative_globs = [str(relative_dir / glob) for glob in filtered]
                ignore_globs.update(relative_globs)

    return ignore_globs


def _read_and_filter(path: Path) -> Set[str]:
    """Reads ignore file and filter comments."""
    raw_lines = [ln.strip() for ln in path.open().readlines()]
    return {ln for ln in raw_lines if not ln.startswith("#")}
