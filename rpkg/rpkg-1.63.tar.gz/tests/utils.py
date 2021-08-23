# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys
import tempfile

import six
from pyrpkg import Commands

# For running tests with Python 2
try:
    import unittest2 as unittest
except ImportError:
    import unittest


# Following global variables are used to construct Commands for tests in this
# module. Only for testing purpose, and they are not going to be used for
# hitting real services.
lookaside = 'http://dist-git-qa.server/repo/pkgs'
lookaside_cgi = 'http://dist-git-qa.server/lookaside/upload.cgi'
gitbaseurl = 'ssh://%(user)s@dist-git-qa.server/rpms/%(module)s'
anongiturl = 'git://dist-git-qa.server/rpms/%(module)s'
lookasidehash = 'md5'
branchre = 'rhel'
kojiconfig = '/path/to/koji.conf'
kojiprofile = 'koji'
build_client = 'koji'

spec_file = '''
Summary: Dummy summary
Name: docpkg
Version: 1.2
Release: 2%{dist}
License: GPL
Source0: https://example.com/readme.patch
#Patch0:
Group: Applications/Productivity
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
%description
Dummy docpkg for tests
%prep
%check
%build
touch README.rst
%clean
rm -rf $$RPM_BUILD_ROOT
%install
rm -rf $$RPM_BUILD_ROOT
%files
%defattr(-,root,root,-)
%doc README.rst
%changelog
* Sat Jun 30 2018 Tester <tester@example.com> - 1.2-2
- Initial version
'''

spec_file_echo_text = '''
Summary: Dummy summary
Name: docpkg
Version: 1.2
Release: 2%{dist}
License: GPL
%{echo:some text}
%{echo:other pkg info}
%description
Dummy docpkg for tests
%prep
%check
%build
touch README.rst
%clean
%install
%files
%defattr(-,root,root,-)
%doc README.rst
%changelog
* Thu Apr 21 2016 Tester <tester@example.com> - 1.2-2
- Initial version
'''


class Assertions(object):

    def get_exists_method(self, search_dir=None):
        if search_dir is None:
            def exists(filename):
                return os.path.exists(filename)
        else:
            def exists(filename):
                return os.path.exists(os.path.join(search_dir, filename))
        return exists

    def assertFilesExist(self, filenames, search_dir=None):
        """Assert existence of files within package repository

        :param filenames: a sequence of file names within package repository to be checked.
        :type filenames: list or tuple
        """
        assert isinstance(filenames, (tuple, list))
        exists = self.get_exists_method(search_dir)
        for filename in filenames:
            self.assertTrue(exists(filename), 'Failure because {0} does not exist'.format(filename))

    def assertFilesNotExist(self, filenames, search_dir=None):
        assert isinstance(filenames, (tuple, list))
        exists = self.get_exists_method(search_dir)
        for filename in filenames:
            self.assertFalse(exists(filename), 'Failure because {0} exists.'.format(filename))


class Utils(object):

    @staticmethod
    def run_cmd(cmd, **kwargs):
        returncode = subprocess.call(cmd, **kwargs)
        if returncode != 0:
            raise RuntimeError('Command fails. Command: %s. Return code %d' % (
                ' '.join(cmd), returncode))

    def redirect_cmd_output(self, cmd, shell=False, env=None, pipe=[], cwd=None):
        if shell:
            cmd = ' '.join(cmd)
        proc_env = os.environ.copy()
        proc_env.update(env or {})
        proc_env['LANG'] = 'en_US.UTF-8'
        proc = subprocess.Popen(cmd, shell=shell, cwd=cwd, env=proc_env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        sys.stdout.write(stdout)
        sys.stderr.write(stderr)

    def read_file(self, filename):
        with open(filename, 'r') as f:
            return f.read()

    def write_file(self, filename, content=''):
        with open(filename, 'w') as f:
            f.write(content)


class RepoCreationMixin(object):
    """Provide methods to create and destroy git repositories for tests"""

    @classmethod
    def create_fake_repos(cls):
        cls.repo_path = tempfile.mkdtemp(prefix='rpkg-commands-tests-')

        cls.spec_file = 'docpkg.spec'

        # Add spec file to this repo and commit
        spec_file_path = os.path.join(cls.repo_path, cls.spec_file)
        with open(spec_file_path, 'w') as f:
            f.write(spec_file)

        git_cmds = [
            ['git', 'init'],
            ['git', 'checkout', '-b', 'master'],
            ['touch', 'sources', 'CHANGELOG.rst'],
            ['git', 'add', spec_file_path, 'sources', 'CHANGELOG.rst'],
            ['git', 'config', 'user.email', 'tester@example.com'],
            ['git', 'config', 'user.name', 'tester'],
            ['git', 'commit', '-m', '"initial commit"'],
            ['git', 'branch', 'eng-rhel-6'],
            ['git', 'branch', 'eng-rhel-6.5'],
            ['git', 'branch', 'eng-rhel-7'],
            ['git', 'branch', 'rhel-6.8'],
            ['git', 'branch', 'rhel-7'],
            ]
        for cmd in git_cmds:
            cls.run_cmd(cmd, cwd=cls.repo_path,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Clone the repo
        cls.cloned_repo_path = tempfile.mkdtemp(prefix='rpkg-commands-tests-cloned-')
        cls.run_cmd(['git', 'clone', cls.repo_path, cls.cloned_repo_path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git_cmds = [
            ['git', 'config', 'user.email', 'tester@example.com'],
            ['git', 'config', 'user.name', 'tester'],
            ['git', 'branch', '--track', 'eng-rhel-6', 'origin/eng-rhel-6'],
            ['git', 'branch', '--track', 'eng-rhel-6.5', 'origin/eng-rhel-6.5'],
            ['git', 'branch', '--track', 'eng-rhel-7', 'origin/eng-rhel-7'],
            ['git', 'branch', '--track', 'rhel-7', 'origin/rhel-7'],
            ]
        for cmd in git_cmds:
            cls.run_cmd(cmd, cwd=cls.cloned_repo_path,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @classmethod
    def destroy_fake_repos(cls):
        shutil.rmtree(cls.repo_path)
        shutil.rmtree(cls.cloned_repo_path)


class CommandTestCase(RepoCreationMixin, Assertions, Utils, unittest.TestCase):

    create_repo_per_test = True
    require_test_repos = True

    @classmethod
    def setUpClass(cls):
        if cls.require_test_repos and not cls.create_repo_per_test:
            cls.create_fake_repos()

    @classmethod
    def tearDownClass(cls):
        if cls.require_test_repos and not cls.create_repo_per_test:
            cls.destroy_fake_repos()

    def setUp(self):
        if self.require_test_repos and self.create_repo_per_test:
            self.create_fake_repos()

    def tearDown(self):
        if self.require_test_repos and self.create_repo_per_test:
            self.destroy_fake_repos()

    def make_commands(self, path=None, user=None, dist=None, target=None, quiet=None):
        """Helper method for creating Commands object for test cases

        This is where you should extend to add more features to support
        additional requirements from other Commands specific test cases.

        Some tests need customize one of user, dist, target, and quiet options
        when creating an instance of Commands. Keyword arguments user, dist,
        target, and quiet here is for this purpose.

        :param str path: path to repository where this Commands will work on
        top of
        :param str user: user passed to --user option
        :param str dist: dist passed to --dist option
        :param str target: target passed to --target option
        :param str quiet: quiet passed to --quiet option
        """
        _repo_path = path if path else self.cloned_repo_path
        return Commands(_repo_path,
                        lookaside, lookasidehash, lookaside_cgi,
                        gitbaseurl, anongiturl,
                        branchre,
                        kojiconfig, build_client,
                        user=user, dist=dist, target=target, quiet=quiet)

    @staticmethod
    def checkout_branch(repo, branch_name):
        """Checkout to a local branch

        :param git.Repo repo: `git.Repo` instance represents a git repository
        that current code works on top of.
        :param str branch_name: name of local branch to checkout
        """
        heads = [head for head in repo.heads if head.name == branch_name]
        assert len(heads) > 0, \
            'Repo must have a local branch named {} that ' \
            'is for running tests. But now, it does not exist. Please check ' \
            'if the repo is correct.'.format(branch_name)

        heads[0].checkout()

    def create_branch(self, repo, branch_name):
        repo.git.branch(branch_name)

    def make_a_dummy_commit(self, repo, filename=None, file_content=None, commit_message=None):
        _filename = os.path.join(repo.working_dir, filename or 'document.txt')
        self.write_file(_filename, file_content or 'Hello rpkg')
        repo.index.add([_filename])
        repo.index.commit(commit_message or 'update document')

    @staticmethod
    def sort_lines(s):
        buf = six.moves.StringIO(s)
        try:
            return sorted((line.strip() for line in buf))
        finally:
            buf.close()


class FakeThreadPool(object):
    """Fake thread pool to run functions sequentially"""

    def __init__(self, processes):
        self.processes = processes

    def map(self, func, iterable):
        return [func(item) for item in iterable]
