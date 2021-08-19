from __future__ import annotations

import imp
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from git import Repo, InvalidGitRepositoryError
from github import Github


def _is_git_repo(path: str = ".", search_parent_directories: bool = True) -> bool:
    try:
        Repo(path, search_parent_directories=search_parent_directories)
        return True
    except InvalidGitRepositoryError:
        return False


def _main_is_frozen() -> bool:
    return (
        hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__")  # new py2exe  # old py2exe
    )  # tools/freeze


def _get_executable_path() -> str:
    if _main_is_frozen():
        # print 'Running from path', os.path.dirname(sys.executable)
        return sys.executable
    return sys.argv[0]


def _relative_path(parent_path, child_path) -> str:
    parent_path = Path(os.path.abspath(parent_path))
    child_path = Path(os.path.abspath(child_path))
    try:
        return str(child_path.relative_to(parent_path)).replace("\\", "/")
    except ValueError:
        return str(child_path)


def _extract_git_version(path: str = ".", search_parent_directories: bool = True) -> Optional[GitVersion]:
    try:
        repo = Repo(path, search_parent_directories=search_parent_directories)
        repository_name = repo.remotes.origin.url.split(".git")[0].split("/")[-1]
        branch_name = repo.active_branch.name
        commit_hash = repo.head.object.hexsha
        commit_comment = repo.head.object.message
        commit_author_name = repo.head.object.author.name
        commit_author_email = repo.head.object.author.email
        entrypoint = _relative_path(os.path.dirname(repo.git_dir), _get_executable_path())
        is_dirty = repo.is_dirty()
        uri = repo.remotes.origin.url
        return GitVersion(
            repository_name,
            branch_name,
            commit_hash,
            commit_comment,
            commit_author_name,
            commit_author_email,
            is_dirty,
            uri,
            entrypoint,
        )
    except InvalidGitRepositoryError:
        return None


def _extract_github_information_from_uri(uri: str) -> Optional[Tuple[str, str, str]]:
    match = re.search("(?:https://github.com/|git@github.com:)([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)(?:/tree/(.+))?", uri)
    if match:
        return match.group(1), match.group(2), match.group(3)
    else:
        return None


def _create_git_version_from_uri(
    uri: str, script_relative_path: Optional[str] = None, login_or_token=None, password=None, jwt=None
):
    g = Github(login_or_token=login_or_token, password=password, jwt=jwt)
    result = _extract_github_information_from_uri(uri)
    if result is None:
        return None
    organisation, repository_name, branch = result
    github_repository = g.get_repo(f"{organisation}/{repository_name}")
    if branch is None:
        branch_name = github_repository.default_branch
    else:
        branch_name = branch
    github_branch = github_repository.get_branch(branch_name)
    commit = github_branch.commit
    if github_branch is None:
        raise RuntimeError(f"invalid branch name {branch_name}")
    return GitVersion(
        repository_name,
        branch_name,
        commit.sha,
        commit.commit.message,
        commit.commit.author.name,
        commit.commit.author.email,
        False,
        f"https://www.github.com/{organisation}/{repository_name}",
        script_relative_path,
    )


@dataclass
class GitVersion:
    repositoryName: str
    branchName: str
    commitHash: str
    commitComment: str
    commitAuthorName: str
    commitAuthorEmail: str
    isDirty: bool
    uri: str
    entrypoint: Optional[str] = None

    @classmethod
    def create(cls, path: str = ".", search_parent_directories: bool = True) -> Optional[GitVersion]:
        return _extract_git_version(path, search_parent_directories)

    @classmethod
    def create_from_github_uri(
        cls, uri: str, script_relative_path: Optional[str] = None, login_or_token=None, password=None, jwt=None
    ):
        return _create_git_version_from_uri(uri, script_relative_path, login_or_token, password, jwt)
