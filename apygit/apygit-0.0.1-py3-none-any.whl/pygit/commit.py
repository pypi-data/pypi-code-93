
import datetime
import functools
import os
import re
import subprocess

import decorators



class AmbiguousCommitBranchException(Exception):
    pass


class CommitFile:
    """ Class encapsulating files part of a particular git commit. """
    def __init__(self, diffline, commit):
        self._diffline = diffline
        pattern = ":(?P<pfilemode>\d+) (?P<filemode>\d+) (?P<psha1>\w+) (?P<sha1>\w+) (?P<status>\w+)\s+(?P<filename>.*)"
        m = re.match(pattern, self._diffline)
        self.sha1 = m.group("sha1")
        self.status = m.group("status")
        self.filename = m.group("filename")
        self.filemode = m.group("filemode")
        self.pfilemode = m.group("pfilemode")
        self.commit = commit

    @property
    def repo(self):
        return self.commit.repo

    @decorators.cached
    def isbinary(self) -> bool:
        """ Determine if this file is a binary """
        output = self.repo.execute(["diff", "--numstat", self.repo.revision(self.commit.sha1)])
        # output looks like (-    - indicates binary):
        # 1       1       path/to/foo.c
        # 27      5       path/to/bar.c
        for line in output.splitlines():
            if self.filename in line:
                if line.startswith("-"):
                    return True
                return False
        return False

    @decorators.cached
    def blob(self) -> str:
        """ Return the file contents as a string. In the case of binary files, we return "". """
        if self.isbinary:
            return ""
        return self.repo.execute(["cat-file", "-p", self.sha1])

    @decorators.cached
    def is_symlink(self) -> bool:
        """ Return True if the file mode is 120000 (symlink)"""
        return "120000" in [self.filemode, self.pfilemode]


@functools.total_ordering
class Commit:
    """
    A class encapsulating a git commit.
    Some expensive methods should employ the @cached decorator.
    """
    re_author_date = (r"^AuthorDate: (.*)$", re.MULTILINE)
    re_commit_date = (r"^CommitDate: (.*)$", re.MULTILINE)
    date_format = r"%a %b %d %H:%M:%S %Y"

    def __init__(self, sha1, repo):
        self.sha1 = sha1
        self.repo = repo

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __eq__(self, other):
        return self.sha1 == other.sha1 and self.timestamp == other.timestamp

    def __hash__(self):
        return hash(f"{self.sha1},{self.timestamp}")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.repo.path}@{self.sha1}>"

    def parse_date(self, date):
        # Parse the timezone separately since strptime doesn't work with %z
        tz_str = int(date.rsplit(" ", 1)[1])
        tz_delta = datetime.timedelta(hours=tz_str/100, minutes=tz_str%100)
        return datetime.datetime.strptime(date.rsplit(" ", 1)[0], self.date_format) + tz_delta

    @decorators.cached
    def timestamp(self):
        # we need to determine if this is the only commit in the repo or not; to do this, we use
        # `git rev-list --count self.sha1`
        # if this is the first commit, then self.repo.revision(self.sha1) will produce abcd123^..abcd123,
        # which is invalid, because there is no abcd123^; in this case, we just need self.sha1 instead
        # or self.repo.revision()
        rev = self.repo.revision(self.sha1)
        out = self.repo.execute(["rev-list", "--count", self.sha1])
        if (int(out.strip()) == 1):
            rev = self.sha1
        out = self.repo.execute(["rev-list", "--timestamp", rev])
        return int(out.split()[0])

    @decorators.cached
    def seqnum(self):
        out = self.repo.execute(["describe", "--tags", "--always", "--match", "init", self.sha1])
        return out.split("-")[1]

    @decorators.cached
    def short(self):
        """ The shortened sha1 reference """
        return self.repo.execute(["rev-parse", "--short", self.sha1]).strip()

    @decorators.cached
    def ismerge(self):
        """
        Determine if the current commit is a merge commit. This is determined
        by finding the number of parent commits.

        Examples:
        $ git cat-file -p f4bf9c3f
        tree 30698de62a2fe1744464aea35e821053c43d2142
        parent 338103bc20da59ad634b8577556f2cbe93380552
        parent 908453dff0fcc454e53cd77e475d8c4efb9c5345

        ...

        $ git cat-file -p c66aafb
        tree 9a2497e3a8ee0481ecaee7094619b20cc338e700
        parent f1c523e2497d5b956bb4184cf7450ceaffaf178e
        ...
        """
        output = self.repo.execute(["cat-file", "-p", self.sha1])
        # if the commit message has a line that starts with "parent",
        # we may accidentally declare this as a mnerge; so, stirp the
        # commit message. we only want to deal with the header.
        output = output[:-len(self.message)]
        return len(re.findall(r"^parent", output, re.MULTILINE)) > 1

    @decorators.cached
    def parent(self):
        """ The parent commit object """
        try:
            sha1 = self.repo.execute(["rev-parse", f"{self.sha1}^"], stderr=subprocess.STDOUT).strip()
        except subprocess.CalledProcessError:
            return None
        return Commit(sha1, self.repo)

    @property
    def branch(self) -> str:
        commit = self
        while not commit.remotes:
            commit = commit.parent
        # at this point, we've found the nearest ancestor that is in origin
        if len(commit.remotes) > 1:
            raise AmbiguousCommitBranchException(", ".join(commit.remotes))
        return commit.remotes[0]

    @decorators.cached
    def remotes(self):
        """ The remote branches this commit has been pushed to. """
        if self.repo.is_bare:
            return self.branches
        _branches = self.repo.execute(["branch", "-r", "--contains", self.sha1]).strip().split("\n")
        _branches = [re.sub(r"^origin/", "", x.strip()) for x in _branches]
        return _branches

    @decorators.cached
    def branches(self):
        """ The list of branches this commit is part of. """
        _branches = self.repo.execute(["branch", "--contains", self.sha1]).strip().split()
        _branches = [x.lstrip(" *") for x in _branches]
        return _branches

    @decorators.cached
    def log(self):
        """ The entire commit log message, excluding git notes """
        return self.repo.execute(["rev-list", "--pretty=fuller", "--max-count=1", "--no-notes", self.sha1])

    @property
    def notes(self):
        """ The git notes associated with this commit """
        try:
            # Send stderr to /dev/null to discard error output when no notes are present.
            devnull = open(os.devnull, "w")
            return self.repo.execute(["notes", "show", self.sha1], stderr=devnull)
        except subprocess.CalledProcessError:
            return None

    @property
    def author(self):
        """ The author's name """
        return re.search(r"\nCommit: (.*) <.*>\n", self.log).group(1).strip()

    @property
    def emailaddr(self):
        """ The author's email address """
        return re.search(r"\nCommit: .* <(.*)>\n", self.log).group(1).strip()

    @property
    def username(self):
        """ The author's username """
        return self.emailaddr.split("@")[0]

    @decorators.cached
    def message(self):
        """ The commit message; this is everything entered by the user during commit time.
        It does not include the git metadata added during `git log` """
        msg = re.search(r"\nCommitDate:[^\n]+\n\n(.*)", self.log, re.MULTILINE | re.DOTALL).group(1)
        return re.sub(r"^(\t|    )", "", msg, 0, re.MULTILINE)

    @decorators.cached
    def affected(self):
        """ The files affected, along with a summary of modifications """
        return self.repo.execute(["diff-tree", "--stat", "--summary", "--find-copies-harder",
            self.repo.revision(self.sha1), "--format=%H"])

    @decorators.cached
    def files(self):
        """ The files affected, (mode, name, contents) """
        diff = self.repo.execute(["diff", "--raw", "--abbrev=40", self.repo.revision(self.sha1)])
        # output looks like this:
        # $ git diff --raw --abbrev=40 f1c523e2497d5b956bb4184cf7450ceaffaf178e^..f1c523e2497d5b956bb4184cf7450ceaffaf178e
        # :100644 100644 c66aafbcacbd2fa09594a97eb7c02af3192ee24a 69088fac8ba1f2dba2a892a0d78ea32daed0c777 M      path/to/foo.c
        # :100644 100644 f4bf9c3f15e3da0f8149aee13afbf125a9ff7783 3bc74defc16e627e22ae8d9b823fde2eb833cbc9 M      path/to/bar.c
        return [CommitFile(line, self) for line in diff.splitlines()]

    @decorators.cached
    def author_date(self):
        match = re.search(self.re_author_date[0], self.log, self.re_author_date[1])
        if match and match.group(1).strip() != "":
            return self.parse_date(match.group(1).strip())
        return None

    @decorators.cached
    def commit_date(self):
        return datetime.datetime.fromtimestamp(self.timestamp)
