import subprocess

from pathlib import Path


class Git:
    """Adding some base git functionality, if available on your system,
    to get a version string from git describe to use in version_helper later on.
    """

    @staticmethod
    def _call_process(*args, **kwargs) -> subprocess.CompletedProcess:
        """Call a process with the given `*args` and `**kwargs`

        :return: A CompletedProcess with captured output (stdout and stderr)
        """
        return subprocess.run(*args, **kwargs, capture_output=True)

    @classmethod
    def exec_path(cls) -> Path:
        """Get the installation path of git or None if it was not found.

        :return: Path object to the git executable or None
        """
        args = ['git', '--exec-path']
        proc = cls._call_process(args)
        if proc.returncode == 0:
            path_str = proc.stdout.strip()
            if type(path_str) is bytes:
                path_str = path_str.decode('utf-8')
            return Path(path_str)

    @classmethod
    def describe(cls, dirty=False, always=False) -> str or None:
        """Find the most recent tag that is reachable from a commit.

        If the tag points to the commit, then only the tag is shown. Otherwise,
        it suffixes the tag name with the number of additional commits on top
        of the tagged object and the abbreviated object name of the most recent commit.

        :param dirty: Append '-dirty', if the working tree has local modifications
        :param always: Show uniquely abbreviated commit object as fallback
        :return: Human-readable object name, describing the current git repository state
        """
        if cls.exec_path() is None:
            return None

        args = ['git', 'describe']
        if dirty:
            args.append('--dirty')
        if always:
            args.append('--always')

        proc = cls._call_process(args)
        if proc.returncode == 0:
            description = proc.stdout.strip()
            if type(description) is bytes:
                description = description.decode('utf-8')
            return description
