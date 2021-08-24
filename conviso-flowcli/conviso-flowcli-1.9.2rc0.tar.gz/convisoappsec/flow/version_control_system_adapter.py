import tempfile
import re
import warnings
from contextlib import suppress


class GitAdapter(object):
    LIST_OPTION = '--list'
    SORT_OPTION = '--sort'
    HEAD_COMMIT = 'HEAD'
    OPTION_WITH_ARG_FMT = '{option}={value}'
    EMPTY_REPOSITORY_HASH = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

    def __init__(self, repository_dir='.', load_remote_repositories_heads=True):
        import git
        self._git_client = git.cmd.Git(repository_dir)
        self._first_commit = None

        if load_remote_repositories_heads:
          self.__load_remote_repositories_heads()


    def tags(self, sort='-committerdate'):
        sort_option = self.OPTION_WITH_ARG_FMT.format(
            option=self.SORT_OPTION,
            value=sort,
        )

        args = (self.LIST_OPTION, sort_option)
        client_output = self._git_client.tag(args)
        tags = client_output.splitlines()
        return tags

    def diff(self, version, another_version):
        version = version or self.EMPTY_REPOSITORY_HASH

        if version == self.EMPTY_REPOSITORY_HASH:
            msg_fmt = """Creating diff comparing revision[{0}]
            and the repository beginning"""

            warnings.warn(
                msg_fmt.format(another_version)
            )

        diff_file = tempfile.TemporaryFile()
        self._git_client.diff(
            version,
            another_version,
            output_stream=diff_file
        )

        return diff_file

    def diff_stats(self, version, another_version):
        version = version or self.EMPTY_REPOSITORY_HASH

        if version == self.EMPTY_REPOSITORY_HASH:
            msg_fmt = """Creating diff stats comparing revision[{0}]
            and the repository beginning"""

            warnings.warn(
                msg_fmt.format(another_version)
            )

        stats_output = tempfile.TemporaryFile()

        self._git_client.diff(
            version,
            another_version,
            '--numstat',
            output_stream=stats_output
        )

        stats_summary = GitDiffNumStatSummary.load(stats_output)
        stats_output.close()

        return stats_summary

    @property
    def first_commit(self):
        if self._first_commit:
            return self._first_commit

        command_output = tempfile.TemporaryFile()

        args = [
            '--reverse',
            "--pretty=%H",
        ]

        self._git_client.log(args, output_stream=command_output)
        command_output.seek(0)
        first_in_bytes = command_output.readline()
        command_output.close()
        first = first_in_bytes.decode()

        return first.strip()

    def commit_is_first(self, commit):
        return commit == self.first_commit

    @property
    def head_commit(self):
        client_output = self._git_client.rev_parse(self.HEAD_COMMIT)
        return client_output.strip()

    @property
    def current_commit(self):
        return self.head_commit

    @property
    def previous_commit(self):
        return self.previous_commit_from(self.current_commit)

    def previous_commit_from(self, commit, offset=1):
        if self.commit_is_first(commit):
            return self.EMPTY_REPOSITORY_HASH

        command_fmt = "{commit}~{offset}"

        command = command_fmt.format(
            commit=commit,
            offset=offset,
        )

        client_output = self._git_client.rev_parse(
            command
        )

        return client_output.strip()

    def show_commit_refs(self, commit):
        with tempfile.TemporaryFile() as client_output:
            self._git_client.show_ref(
                "--head", "--heads", "--tags", output_stream=client_output
            )
            refs = _read_file_lines_generator(client_output)
            refs = list(
                filter(
                    lambda ref: re.search(commit, ref),
                    refs,
                )
            )

            return refs

    def show_commit_from_tag(self, tag):
        client_output = self._git_client.rev_parse(
            tag
        )

        return client_output.strip()

    @property
    def empty_repository_tree_commit(self):
        return self.EMPTY_REPOSITORY_HASH

    @property
    def remote_repositories_name(self):
        args = ("show")
        client_output = self._git_client.remote(args)
        repositories = client_output.splitlines()
        return repositories

    def __load_remote_repositories_heads(self):
        heads_refspec_format = "refs/heads/*:refs/remotes/{remote_repository_name}/*"

        for remote_repository_name in self.remote_repositories_name:
            heads_refspec = heads_refspec_format.format(
                remote_repository_name=remote_repository_name
            )

            args = (remote_repository_name, heads_refspec)
            self._git_client.fetch(args)


def _read_file_lines_generator(file):
    file.seek(0)

    while True:
        line = file.readline()
        line = line.decode().strip()

        if line:
            yield line
        else:
            break


class InvalidGitDiffNumStatLineValueException(ValueError):
    pass


class GitDiffNumStatLine(object):
    ADDED_LINES_POSITION = 1
    DELETED_LINES_POSITION = 2
    FILE_PATH_POSITION = 3

    # (added_lines) (deleted_lines) (file_path)
    SRC_LINE_REGEX = r'(\d+)\s+(\d+)\s+(.*)'
    BIN_LINE_REGEX = r'(-)\s+(-)\s+(.*)'

    def __init__(self, added_lines, deleted_lines, file_path):
        self.added_lines = added_lines
        self.deleted_lines = deleted_lines
        self.file_path = file_path

    @classmethod
    def parse(cls, raw_line):
        with suppress(AttributeError):
            match = re.match(cls.SRC_LINE_REGEX, raw_line)
            group = match.group

            added_lines_str = group(cls.ADDED_LINES_POSITION)
            deleted_lines_str = group(cls.DELETED_LINES_POSITION)
            file_path = group(cls.FILE_PATH_POSITION)

            added_lines = int(added_lines_str)
            deleted_lines = int(deleted_lines_str)

            return cls(added_lines, deleted_lines, file_path)

        with suppress(AttributeError):
            match = re.match(cls.BIN_LINE_REGEX, raw_line)

            file_path = match.group(cls.FILE_PATH_POSITION)

            return cls(0, 0, file_path)

        error_msg_fmt = '\n'.join([
            'The expected git diff numstat line format are:',
            'Expected format: {src_fmt}',
            'Expected format: {bin_fmt}',
            'Given value: {given}',
        ])

        msg = error_msg_fmt.format(
            src_fmt=cls.SRC_LINE_REGEX,
            bin_fmt=cls.BIN_LINE_REGEX,
            given=raw_line
        )

        raise InvalidGitDiffNumStatLineValueException(msg)

    @classmethod
    def load(cls, numstat_fh):
        numstat_fh.seek(0)

        while True:
            line = numstat_fh.readline()

            with suppress(AttributeError):
                line = line.decode()

            if line:
                yield cls.parse(line)
                continue

            break


class GitDiffNumStatSummary(object):

    def __init__(self):
        self.added_lines = 0
        self.deleted_lines = 0
        self.changed_files = []

    def _add_numstat_lines(self, numstat_lines):
        for numstat_line in numstat_lines:
            self._add_numstat_line(numstat_line)

    def _add_numstat_line(self, numstat_line):
        self._add_added_lines(numstat_line.added_lines)
        self._add_deleted_lines(numstat_line.deleted_lines)
        self._add_changed_files(numstat_line.file_path)

    def _add_added_lines(self, added_lines):
        self.added_lines += added_lines

    def _add_deleted_lines(self, deleted_lines):
        self.deleted_lines += deleted_lines

    def _add_changed_files(self, changed_file):
        self.changed_files.append(
            changed_file
        )

    @property
    def changed_lines(self):
        return self.added_lines + self.deleted_lines

    @classmethod
    def load(cls, numstat_fh):
        git_diffnumstat_lines = GitDiffNumStatLine.load(numstat_fh)
        summary = cls()
        summary._add_numstat_lines(git_diffnumstat_lines)

        return summary

    @property
    def dict(self):
        field_names = [
            'added_lines',
            'deleted_lines',
            'changed_lines',
            'changed_files',
        ]

        fields = {
            name: getattr(self, name) for name in field_names
        }

        return fields
