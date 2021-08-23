
import logging
import os
import re
import subprocess

import commit
import decorators


def execute(args: list, decode: str = None, cmd: str = "git", **subprocess_kwargs) -> str:
    """ Execute a git command """
    cmd = [cmd] + args
    logging.debug(f"execute: {' '.join(cmd)}")
    out = subprocess.check_output(cmd, **subprocess_kwargs).strip()
    decode = decode or "UTF-8"
    out = out.decode(decode)
    logging.debug(out)
    return out


def revision(rev1: str, rev2: str = None) -> str:
    """ Convert 1 or 2 sha1 into a revision suitable for git commands """
    if rev2:
        return f"{rev1}..{rev2}"
    if not rev2 and '..' in rev1:
        return rev1  # already a valid revision
    return rev1



class Repository:
    def __init__(self, path: str, **kwargs):
        self.path = os.path.realpath(os.path.expanduser(path))
        self.stash = None
        self.hooks = None

        try:
            self.rootdir
        except Exception as e:
            raise

    def revision(self, rev1: str, rev2: str = None) -> str:
        return revision(rev1, rev2)

    def execute(self, args, cmd="git", **kwargs) -> str:
        kwargs["cwd"] = self.path
        return execute(args, cmd=cmd, **kwargs)

    @decorators.cached
    def is_bare(self) -> bool:
        return self.execute(["rev-parse", "--is-bare-repository"]) == "true"

    @decorators.cached
    def rootdir(self) -> str:
        if self.is_bare:
            d = self.execute(["rev-parse", "--git-dir"])
            if d == ".":
                d = self.execute([], cmd="pwd")
            return d
        return self.execute(["rev-parse", "--show-toplevel"])

    @decorators.cached
    def gitdir(self) -> str:
        if self.is_bare:
            return self.rootdir
        return os.path.join(self.rootdir, ".git")

    def status(self):
        if self.is_bare:
            raise Exception("Cannot get git status for bare repo")
        out = self.execute(["status", "--short"])
        if out == "":
            return []
        return [(x[2:].strip(), x[0:2].strip()) for x in out.split("\n")]

    @decorators.cached
    def default_upstream_branch(self):
        output = self.execute(["branch", "-r", "--list", "origin/HEAD"])
        return re.sub(".* -> origin/", "", output)

    @property
    def branch(self):
        return self.execute(["branch", "--show-current"])

    @property
    def is_dirty(self):
        return len(self.status()) != 0

    def commit(self, rev1: str = "HEAD"):
        return commit.Commit(rev1, self)

    def commits(self, rev1: str = None, rev2: str = None):
        rev1 = rev1 or "HEAD"
        if rev1 == "0000000000000000000000000000000000000000":  # branch creation
            rev1 = rev2
            rev2 = None
        _commits = self.execute(["rev-list", revision(rev1, rev2)])
        # When switching to a branch is that older than the current, git
        # hooks may be called with rev1 > rev2, in that case, we should
        # return an empty list. "".split('\n') returns a list with an empty
        # string, which is not what we want.
        return [self.commit(x) for x in _commits.split("\n") if x]
