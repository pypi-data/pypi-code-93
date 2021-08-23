# -*- coding: utf-8 -*-

import errno
import filecmp
import glob
import hashlib
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile

import git
import koji_cli.lib
import six
import utils
from mock import ANY, Mock, PropertyMock, call, mock_open, patch
from six.moves import StringIO, configparser, http_client
from utils import CommandTestCase, FakeThreadPool

import pyrpkg.cli
from pyrpkg import Commands, Modulemd, layout, rpkgError
from pyrpkg.errors import AlreadyUploadedError

try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    import openidc_client
except ImportError:
    openidc_client = None


fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
# rpkg.conf for running tests below
config_file = os.path.join(fixtures_dir, 'rpkg.conf')

fake_spec_content = '''
Summary: package demo
Name: pkgtool
Version: 0.1
Release: 1%{?dist}
License: GPL
%description
package demo for testing
%changelog
* Mon Nov 07 2016 tester@example.com
- first release 0.1
- add new spec
'''

if six.PY2:
    ConfigParser = configparser.SafeConfigParser
else:
    # The SafeConfigParser class has been renamed to ConfigParser in Python 3.2.
    ConfigParser = configparser.ConfigParser

KOJI_UNIQUE_PATH_REGEX = r'^cli-build/\d+\.\d+\.[a-zA-Z]+$'


def mock_get_rpm_package_name(self, rpm_file):
    return(os.path.basename(rpm_file)[:-len('.src.rpm')])


class MockLayout(layout.DistGitLayout):
    def is_retired(self):
        return None


class CliTestCase(CommandTestCase):

    def new_cli(self, cfg=None):
        config = ConfigParser()
        config.read(cfg or config_file)

        client = pyrpkg.cli.cliClient(config, name='rpkg')
        client.setupLogging(pyrpkg.log)
        pyrpkg.log.setLevel(logging.CRITICAL)
        client.do_imports()
        client.parse_cmdline()

        return client

    def make_changes(self, repo=None, untracked=None, commit=None, filename=None, content=''):
        repo_path = repo or self.cloned_repo_path
        _filename = filename or 'new-file.txt'

        self.write_file(os.path.join(repo_path, _filename), content)

        cmds = []
        if not untracked:
            cmds.append(['git', 'add', _filename])
        if not untracked and commit:
            cmds.append(['git', 'commit', '-m', 'Add new file {0}'.format(_filename)])

        for cmd in cmds:
            self.run_cmd(cmd, cwd=repo_path,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def get_absolute_conf_filename(self, filename):
        """Find and return absolute conf file from fixtures"""
        abs_filename = os.path.join(
            os.path.dirname(__file__), 'fixtures', filename)
        if not os.path.exists(abs_filename):
            raise RuntimeError(
                'Fixture conf file {0} does not exist.'.format(abs_filename))
        return abs_filename


class TestContainerBuildWithKoji(CliTestCase):
    """Test container_build with koji"""

    create_repo_per_test = False

    def setUp(self):
        super(TestContainerBuildWithKoji, self).setUp()
        self.checkout_branch(git.Repo(self.cloned_repo_path), 'eng-rhel-7')
        self.container_build_koji_patcher = patch(
            'pyrpkg.Commands.container_build_koji')
        self.mock_container_build_koji = \
            self.container_build_koji_patcher.start()

    def tearDown(self):
        self.container_build_koji_patcher.stop()
        super(TestContainerBuildWithKoji, self).tearDown()

    def test_using_kojiprofile(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'container-build']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.container_build_koji()

        self.mock_container_build_koji.assert_called_once_with(
            False,
            opts={
                'scratch': False,
                'quiet': False,
                'release': None,
                'isolated': False,
                'koji_parent_build': None,
                'yum_repourls': None,
                'dependency_replacements': None,
                'git_branch': 'eng-rhel-7',
                'arches': None,
                'signing_intent': None,
                'compose_ids': None,
                'skip_build': False
            },
            kojiprofile='koji',
            build_client=utils.build_client,
            koji_task_watcher=koji_cli.lib.watch_tasks,
            nowait=False,
            flatpak=False
        )

    def test_override_target(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'container-build',
                   '--target', 'f25-docker-candidate']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.container_build_koji()

        self.assertEqual('f25-docker-candidate', cli.cmd._target)
        self.mock_container_build_koji.assert_called_once_with(
            True,
            opts={
                'scratch': False,
                'quiet': False,
                'release': None,
                'isolated': False,
                'koji_parent_build': None,
                'yum_repourls': None,
                'dependency_replacements': None,
                'git_branch': 'eng-rhel-7',
                'arches': None,
                'signing_intent': None,
                'compose_ids': None,
                'skip_build': False
            },
            kojiprofile='koji',
            build_client=utils.build_client,
            koji_task_watcher=koji_cli.lib.watch_tasks,
            nowait=False,
            flatpak=False
        )

    def test_mutiple_arguments_repo_url(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'container-build',
                   '--target', 'f34-container-candidate', '--scratch',
                   '--repo-url', 'a', 'b', '--repo-url', 'c']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.container_build_koji()

        self.assertEqual('f34-container-candidate', cli.cmd._target)
        self.mock_container_build_koji.assert_called_once_with(
            True,
            opts={
                'scratch': True,
                'quiet': False,
                'release': None,
                'isolated': False,
                'koji_parent_build': None,
                'yum_repourls': ['a', 'b', 'c'],
                'dependency_replacements': None,
                'git_branch': 'eng-rhel-7',
                'arches': None,
                'signing_intent': None,
                'compose_ids': None,
                'skip_build': False
            },
            kojiprofile='koji',
            build_client=utils.build_client,
            koji_task_watcher=koji_cli.lib.watch_tasks,
            nowait=False,
            flatpak=False
        )

    def test_mutiple_arguments_compose_ids(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'container-build',
                   '--target', 'f34-container-candidate', '--scratch',
                   '--compose-id', '1', '2', '--compose-id', '3']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.container_build_koji()

        self.mock_container_build_koji.assert_called_once_with(
            True,
            opts={
                'scratch': True,
                'quiet': False,
                'release': None,
                'isolated': False,
                'koji_parent_build': None,
                'yum_repourls': None,
                'dependency_replacements': None,
                'git_branch': 'eng-rhel-7',
                'arches': None,
                'signing_intent': None,
                'compose_ids': [1, 2, 3],
                'skip_build': False
            },
            kojiprofile='koji',
            build_client=utils.build_client,
            koji_task_watcher=koji_cli.lib.watch_tasks,
            nowait=False,
            flatpak=False
        )

    def test_isolated(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'container-build',
                   '--isolated', '--build-release', '99']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.container_build_koji()

        self.mock_container_build_koji.assert_called_once_with(
            False,
            opts={
                'scratch': False,
                'quiet': False,
                'release': '99',
                'isolated': True,
                'koji_parent_build': None,
                'yum_repourls': None,
                'dependency_replacements': None,
                'git_branch': 'eng-rhel-7',
                'arches': None,
                'signing_intent': None,
                'compose_ids': None,
                'skip_build': False
            },
            kojiprofile='koji',
            build_client=utils.build_client,
            koji_task_watcher=koji_cli.lib.watch_tasks,
            nowait=False,
            flatpak=False
        )

    def test_use_container_build_own_config(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'container-build']
        cfg_file = os.path.join(os.path.dirname(__file__),
                                'fixtures',
                                'rpkg-container-own-config.conf')

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli(cfg_file)
            cli.container_build_koji()

        args, kwargs = self.mock_container_build_koji.call_args
        self.assertEqual('koji-container', kwargs['kojiprofile'])
        self.assertEqual('koji', kwargs['build_client'])

    @unittest.skipIf(
        Modulemd is None,
        'Skip on old Python versions where libmodulemd is not available.')
    @patch('requests.get')
    def test_flatpak(self, mock_get):
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }

        mock_get.return_value = mock_rv

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'flatpak-build']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.flatpak_build()

        self.mock_container_build_koji.assert_called_once_with(
            False,
            opts={
                'scratch': False,
                'quiet': False,
                'release': None,
                'isolated': False,
                'koji_parent_build': None,
                'git_branch': 'eng-rhel-7',
                'arches': None,
                'signing_intent': None,
                'skip_build': False,
                'yum_repourls': None
            },
            kojiprofile='koji',
            build_client=utils.build_client,
            koji_task_watcher=koji_cli.lib.watch_tasks,
            nowait=False,
            flatpak=True
        )


class TestClog(CliTestCase):

    create_repo_per_test = False

    def setUp(self):
        super(TestClog, self).setUp()
        self.checkout_branch(git.Repo(self.cloned_repo_path), 'eng-rhel-6')

    def cli_clog(self):
        """Run clog command"""
        cli = self.new_cli()
        cli.clog()

    def test_clog(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'clog']

        with patch('sys.argv', new=cli_cmd):
            self.cli_clog()

        clog_file = os.path.join(self.cloned_repo_path, 'clog')
        self.assertTrue(os.path.exists(clog_file))
        clog = self.read_file(clog_file).strip()
        self.assertEqual('Initial version', clog)

    def test_raw_clog(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'clog', '--raw']

        with patch('sys.argv', new=cli_cmd):
            self.cli_clog()

        clog_file = os.path.join(self.cloned_repo_path, 'clog')
        self.assertTrue(os.path.exists(clog_file))
        clog = self.read_file(clog_file).strip()
        self.assertEqual('- Initial version', clog)

    def test_reference_source_files_in_spec_should_not_break_clog(self):
        """SPEC containing Source0 or Patch0 should not break clog

        This case is reported in bug 1412224
        """
        spec_file = os.path.join(self.cloned_repo_path, self.spec_file)
        spec = self.read_file(spec_file)
        self.write_file(spec_file, spec.replace('#Source0:', 'Source0: extrafile.txt'))
        self.test_raw_clog()


class TestCommit(CliTestCase):

    def setUp(self):
        super(TestCommit, self).setUp()
        self.checkout_branch(git.Repo(self.cloned_repo_path), 'eng-rhel-6')
        self.make_changes()

    def get_last_commit_message(self):
        repo = git.Repo(self.cloned_repo_path)
        return six.next(repo.iter_commits()).message.strip()

    def cli_commit(self):
        """Run commit command"""
        cli = self.new_cli()
        cli.commit()

    def test_with_only_summary(self):
        cli = ['rpkg', '--path', self.cloned_repo_path, 'commit', '-m', 'new release']

        with patch('sys.argv', new=cli):
            self.cli_commit()

        commit_msg = self.get_last_commit_message()
        self.assertEqual('new release', commit_msg)

    def test_with_summary_and_changelog(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'commit', '-m', 'new release', '--with-changelog']

        with patch('sys.argv', new=cli_cmd):
            self.cli_commit()

        commit_msg = self.get_last_commit_message()
        expected_commit_msg = '''new release

Initial version'''
        self.assertEqual(expected_commit_msg, commit_msg)
        self.assertFalse(os.path.exists(os.path.join(self.cloned_repo_path, 'clog')))
        self.assertFalse(os.path.exists(os.path.join(self.cloned_repo_path, 'commit-message')))

    def test_with_clog(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'commit', '--clog']

        with patch('sys.argv', new=cli_cmd):
            self.cli_commit()

        commit_msg = self.get_last_commit_message()
        expected_commit_msg = 'Initial version'
        self.assertEqual(expected_commit_msg, commit_msg)
        self.assertFalse(os.path.exists(os.path.join(self.cloned_repo_path, 'clog')))

    def test_with_raw_clog(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'commit', '--clog', '--raw']
        with patch('sys.argv', new=cli_cmd):
            self.cli_commit()

        commit_msg = self.get_last_commit_message()
        expected_commit_msg = '- Initial version'
        self.assertEqual(expected_commit_msg, commit_msg)
        self.assertFalse(os.path.exists(os.path.join(self.cloned_repo_path, 'clog')))

    def test_cannot_use_with_changelog_without_a_summary(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'commit', '--with-changelog']

        with patch('sys.argv', new=cli_cmd):
            self.assertRaises(rpkgError, self.cli_commit)

    def test_push_after_commit(self):
        repo = git.Repo(self.cloned_repo_path)
        self.checkout_branch(repo, 'eng-rhel-6')

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'commit', '-m', 'new release', '--with-changelog', '--push']

        with patch('sys.argv', new=cli_cmd):
            self.cli_commit()

        diff_commits = repo.git.rev_list('origin/master...master')
        self.assertEqual('', diff_commits)

    def test_signoff(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'commit', '-m', 'new release', '-s']

        with patch('sys.argv', new=cli_cmd):
            self.cli_commit()

            commit_msg = self.get_last_commit_message()
            self.assertTrue('Signed-off-by:' in commit_msg)


class TestPull(CliTestCase):

    def test_pull(self):
        self.make_changes(repo=self.repo_path, commit=True)

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'pull']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.pull()

        origin_last_commit = str(six.next(git.Repo(self.repo_path).iter_commits()))
        cloned_last_commit = str(six.next(cli.cmd.repo.iter_commits()))
        self.assertEqual(origin_last_commit, cloned_last_commit)

    def test_pull_rebase(self):
        self.make_changes(repo=self.repo_path, commit=True)
        self.make_changes(repo=self.cloned_repo_path, commit=True,
                          filename='README.rst', content='Hello teseting.')

        origin_last_commit = str(six.next(git.Repo(self.repo_path).iter_commits()))

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'pull', '--rebase']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.pull()

        commits = cli.cmd.repo.iter_commits()
        six.next(commits)
        fetched_commit = str(six.next(commits))
        self.assertEqual(origin_last_commit, fetched_commit)
        self.assertEqual('', cli.cmd.repo.git.log('--merges'))


class TestClone(CliTestCase):
    """Test clone command"""

    @patch('sys.stderr', new=StringIO())
    def test_repo_arg(self):
        """repo argument should contain just a name of the repo, not URL
        and program should raise exception during argument parsing"""
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'clone', 'ssh://git@pagure.io/forks/user/xrepo.git', 'target_dir']

        with patch('sys.argv', new=cli_cmd):
            with self.assertRaises(SystemExit):
                cli = self.new_cli()
                cli.clone()  # this is not gonna be called

        output = sys.stderr.getvalue().strip()
        self.assertIn("argument can't contain an URL", output)

    @patch('sys.stderr', new=StringIO())
    @patch('pyrpkg.Commands._clone_config', new_callable=Mock())
    @patch('pyrpkg.Commands._run_command')
    def test_extra_args(self, _run_command, _clone_config):
        cli_cmd = ['rpkg', '--user', 'dude', '--path', self.cloned_repo_path,
                   'clone', 'repository_name', '--', '--progress']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.clone()

        expected_cmd = ['git', 'clone', 'ssh://dude@localhost/repository_name',
                        '--origin', 'origin', '--progress']
        _run_command.assert_called_once_with(expected_cmd,
                                             cwd=self.cloned_repo_path)
        output = sys.stderr.getvalue().strip()
        self.assertEqual('', output)

    @patch('sys.stderr', new=StringIO())
    @patch('pyrpkg.Commands._clone_config', new_callable=Mock())
    @patch('pyrpkg.Commands._run_command')
    def test_extra_args_incorrect(self, _run_command, _clone_config):
        """Missing '--' separator between standard arguments and extra
        arguments. This can be valid command but might have different
        and unexpected behaviour. Warning is shown."""

        cli_cmd = ['rpkg', '--user', 'dude', '--path', self.cloned_repo_path,
                   'clone', 'repository_name', '--progress']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.clone()

        expected_cmd = ['git', 'clone', 'ssh://dude@localhost/repository_name',
                        '--origin', 'origin', '--progress']
        _run_command.assert_called_once_with(expected_cmd,
                                             cwd=self.cloned_repo_path)
        output = sys.stderr.getvalue().strip()
        self.assertIn('extra_args in the command are not separated', output)


class TestSrpm(CliTestCase):
    """Test srpm command"""

    @patch('pyrpkg.Commands._run_command')
    def test_srpm(self, _run_command):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6', 'srpm']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.srpm()

        expected_cmd = ['rpmbuild'] + cli.cmd.rpmdefines + \
            ['--nodeps', '-bs', os.path.join(cli.cmd.path, cli.cmd.spec)]
        _run_command.assert_called_once_with(expected_cmd, shell=True)

    @patch('pyrpkg.Commands._run_command')
    def test_srpm_with_options(self, _run_command):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6', 'srpm',
                   '--define', '"macro1 meansthis"']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.srpm()

        expected_cmd = ['rpmbuild'] + cli.cmd.rpmdefines + \
            ['--define', '"macro1 meansthis"', '--nodeps', '-bs',
             os.path.join(cli.cmd.path, cli.cmd.spec)]
        _run_command.assert_called_once_with(expected_cmd, shell=True)

    @patch('pyrpkg.Commands._run_command')
    def test_srpm_with_extra_args(self, _run_command):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6', 'srpm',
                   '--', '--define', '"name body"', '--undefine', 'python']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.srpm()

        expected_cmd = ['rpmbuild'] + cli.cmd.rpmdefines + \
            ['--define', '"name body"', '--undefine', 'python', '--nodeps', '-bs',
             os.path.join(cli.cmd.path, cli.cmd.spec)]
        _run_command.assert_called_once_with(expected_cmd, shell=True)


class TestCompile(CliTestCase):

    create_repo_per_test = False

    @patch('pyrpkg.Commands._run_command')
    def test_compile(self, _run_command):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6', 'compile']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.compile()

        spec = os.path.join(cli.cmd.path, cli.cmd.spec)
        rpmbuild = ['rpmbuild'] + cli.cmd.rpmdefines + ['-bc', spec]

        _run_command.assert_called_once_with(rpmbuild, shell=True)

    @patch('pyrpkg.Commands._run_command')
    def test_compile_with_options(self, _run_command):
        builddir = os.path.join(self.cloned_repo_path, 'builddir')

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6', '-q', 'compile',
                   '--builddir', builddir, '--short-circuit', '--arch', 'i686', '--nocheck',
                   '--define', 'macro1 meansthis', '--', '--rmspec']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.compile()

        spec = os.path.join(cli.cmd.path, cli.cmd.spec)
        rpmbuild = ['rpmbuild'] + cli.cmd.rpmdefines + \
            ["--define '_builddir %s'" % builddir, '--target', 'i686',
             '--define', 'macro1 meansthis', '--rmspec', '--short-circuit',
             '--nocheck', '--quiet', '-bc', spec]

        _run_command.assert_called_once_with(rpmbuild, shell=True)


class TestPrep(CliTestCase):

    create_repo_per_test = False

    @patch('pyrpkg.Commands._run_command')
    def test_prep(self, _run_command):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6', 'prep']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.prep()

        spec = os.path.join(cli.cmd.path, cli.cmd.spec)
        rpmbuild = ['rpmbuild'] + cli.cmd.rpmdefines + ['--nodeps', '-bp', spec]
        _run_command.assert_called_once_with(rpmbuild, shell=True)

    @patch('pyrpkg.Commands._run_command')
    def test_prep_with_options(self, _run_command):
        builddir = os.path.join(self.cloned_repo_path, 'builddir')
        buildrootdir = os.path.join(self.cloned_repo_path, 'buildrootdir')

        cli_cmd = [
            'rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6',
            '-q', 'compile', '--arch', 'i686', '--builddir', builddir,
            '--buildrootdir', buildrootdir, '--', '-v'
        ]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.prep()

        spec = os.path.join(cli.cmd.path, cli.cmd.spec)
        rpmbuild = ['rpmbuild'] + cli.cmd.rpmdefines + [
            "--define '_builddir %s'" % builddir, '--target', 'i686', '-v',
            '--quiet', "--define '_buildrootdir %s'" % buildrootdir,
            '--nodeps', '-bp', spec
        ]
        _run_command.assert_called_once_with(rpmbuild, shell=True)


class TestInstall(CliTestCase):

    create_repo_per_test = False

    @patch('pyrpkg.Commands._run_command')
    def test_install(self, _run_command):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6', 'install']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.install()

        spec = os.path.join(cli.cmd.path, cli.cmd.spec)
        rpmbuild = ['rpmbuild'] + cli.cmd.rpmdefines + ['-bi', spec]

        _run_command.assert_called_once_with(rpmbuild, shell=True)

    @patch('pyrpkg.Commands._run_command')
    def test_install_with_options(self, _run_command):
        builddir = os.path.join(self.cloned_repo_path, 'builddir')
        buildrootdir = os.path.join(self.cloned_repo_path, 'buildrootdir')

        cli_cmd = [
            'rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6',
            '-q', 'install', '--nocheck', '--arch', 'i686',
            '--builddir', builddir, '--buildrootdir', buildrootdir
        ]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.install()

        spec = os.path.join(cli.cmd.path, cli.cmd.spec)
        rpmbuild = ['rpmbuild'] + cli.cmd.rpmdefines + [
            "--define '_builddir %s'" % builddir, '--target', 'i686',
            '--nocheck', '--quiet',
            "--define '_buildrootdir %s'" % buildrootdir,
            '-bi', spec
        ]

        _run_command.assert_called_once_with(rpmbuild, shell=True)


class TestLocal(CliTestCase):

    create_repo_per_test = False

    @patch('pyrpkg.subprocess.check_call')
    def test_local(self, check_call):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6', 'local']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.local()

        spec = os.path.join(cli.cmd.path, cli.cmd.spec)
        rpmbuild = ['rpmbuild'] + cli.cmd.rpmdefines + ['-ba', spec]
        tee = ['tee', '.build-%s-%s.log' % (cli.cmd.ver, cli.cmd.rel)]
        cmd = '%s 2>&1 | %s; exit "${PIPESTATUS[0]} ${pipestatus[1]}"' % (
            ' '.join(rpmbuild), ' '.join(tee)
        )
        check_call.assert_called_once_with(cmd, shell=True)

    @patch('pyrpkg.subprocess.check_call')
    def test_local_with_options(self, check_call):
        builddir = os.path.join(self.cloned_repo_path, 'this-builddir')
        buildrootdir = os.path.join(self.cloned_repo_path, 'this-buildrootdir')

        cli_cmd = [
            'rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6',
            '-q', 'local', '--builddir', builddir, '--arch', 'i686',
            '--with', 'a', '--without', 'b', '--buildrootdir', buildrootdir,
            '--', '--clean']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.local()

        spec = os.path.join(cli.cmd.path, cli.cmd.spec)
        rpmbuild = ['rpmbuild'] + cli.cmd.rpmdefines + [
            '--with', 'a', '--without', 'b',
            "--define '_builddir %s'" % builddir,
            '--target', 'i686', '--clean', '--quiet',
            "--define '_buildrootdir %s'" % buildrootdir,
            '-ba', spec
        ]
        tee = ['tee', '.build-%s-%s.log' % (cli.cmd.ver, cli.cmd.rel)]

        cmd = '%s 2>&1 | %s; exit "${PIPESTATUS[0]} ${pipestatus[1]}"' % (
            ' '.join(rpmbuild), ' '.join(tee)
        )

        check_call.assert_called_once_with(cmd, shell=True)


class TestVerifyFiles(CliTestCase):

    create_repo_per_test = False

    @patch('pyrpkg.Commands._run_command')
    def test_verify_files(self, _run_command):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6', 'verify-files']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.verify_files()

        spec = os.path.join(cli.cmd.path, cli.cmd.spec)
        rpmbuild = ['rpmbuild'] + cli.cmd.rpmdefines + ['-bl', spec]
        _run_command.assert_called_once_with(rpmbuild, shell=True)

    @patch('pyrpkg.Commands._run_command')
    def test_verify_files_with_options(self, _run_command):
        builddir = os.path.join(self.cloned_repo_path, 'this-builddir')
        buildrootdir = os.path.join(self.cloned_repo_path, 'this-buildrootdir')

        cli_cmd = [
            'rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6',
            '-q', 'verify-files', '--builddir', builddir,
            '--buildrootdir', buildrootdir
        ]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.verify_files()

        spec = os.path.join(cli.cmd.path, cli.cmd.spec)
        rpmbuild = ['rpmbuild'] + cli.cmd.rpmdefines + [
            "--define '_builddir %s'" % builddir,
            '--quiet',
            "--define '_buildrootdir %s'" % buildrootdir,
            '-bl', spec
        ]
        _run_command.assert_called_once_with(rpmbuild, shell=True)


class TestVerrel(CliTestCase):

    create_repo_per_test = False

    @patch('sys.stdout', new=StringIO())
    def test_verrel_get_repo_name_from_spec(self):
        cli_cmd = ['rpkg', '--path', self.repo_path, '--release', 'rhel-6', 'verrel']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.verrel()

        output = sys.stdout.getvalue().strip()
        self.assertEqual('docpkg-1.2-2.el6', output)

    @patch('sys.stdout', new=StringIO())
    def test_verrel(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, '--release', 'rhel-6', 'verrel']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.verrel()

        repo_name = os.path.basename(self.repo_path)
        output = sys.stdout.getvalue().strip()
        self.assertEqual('{0}-1.2-2.el6'.format(repo_name), output)


class TestSwitchBranch(CliTestCase):

    @patch('sys.stdout', new=StringIO())
    def test_list_branches(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'switch-branch']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.switch_branch()

        output = sys.stdout.getvalue()

        # Not test all branches listed, just test part of them.
        strings = ('Locals', 'Remotes', 'eng-rhel-6', 'origin/eng-rhel-6')
        for string in strings:
            self.assertTrue(string in output)

    def test_switch_branch_tracking_remote_branch(self):
        repo = git.Repo(self.cloned_repo_path)

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'switch-branch', 'rhel-6.8']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.switch_branch()

        self.assertEqual('rhel-6.8', repo.active_branch.name)

        # Ensure local branch is tracking remote branch
        self.assertEqual('refs/heads/rhel-6.8', repo.git.config('branch.rhel-6.8.merge'))

    def test_switch_local_branch(self):
        repo = git.Repo(self.cloned_repo_path)
        self.checkout_branch(repo, 'master')

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'switch-branch', 'eng-rhel-6']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.switch_branch()

        self.assertEqual('eng-rhel-6', repo.active_branch.name)

    def test_fail_on_dirty_repo(self):
        repo = git.Repo(self.cloned_repo_path)
        self.checkout_branch(repo, 'eng-rhel-6')

        self.make_changes()

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'switch-branch', 'master']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            try:
                cli.switch_branch()
            except rpkgError as e:
                expected_msg = '{0} has uncommitted changes'.format(self.cloned_repo_path)
                self.assertTrue(expected_msg in str(e))
            else:
                self.fail('switch branch on dirty repo should fail.')

    def test_fail_switch_unknown_remote_branch(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'switch-branch',
                   'unknown-remote-branch']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            try:
                cli.switch_branch()
            except rpkgError as e:
                self.assertEqual('Unknown remote branch origin/unknown-remote-branch', str(e))
            else:
                self.fail('Switch to unknown remote branch should fail.')


class TestUnusedPatches(CliTestCase):

    def setUp(self):
        super(TestUnusedPatches, self).setUp()

        self.patches = (
            os.path.join(self.cloned_repo_path, '0001-add-new-feature.patch'),
            os.path.join(self.cloned_repo_path, '0002-hotfix.patch'),
        )
        for patch_file in self.patches:
            self.write_file(patch_file)
        git.Repo(self.cloned_repo_path).index.add(self.patches)

    @patch('sys.stdout', new=StringIO())
    def test_list_unused_patches(self):
        self.checkout_branch(git.Repo(self.cloned_repo_path), 'eng-rhel-6')

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'unused-patches']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.unused_patches()

        output = sys.stdout.getvalue().strip()
        expected_patches = [os.path.basename(patch_file) for patch_file in self.patches]
        self.assertEqual('\n'.join(expected_patches), output)


class TestDiff(CliTestCase):

    def setUp(self):
        super(TestDiff, self).setUp()

        with open(os.path.join(self.cloned_repo_path, self.spec_file), 'a') as f:
            f.write('- upgrade dependencies')

        self.make_changes()

    @patch('pyrpkg.Commands._run_command')
    @patch('pyrpkg.os.chdir')
    def test_diff(self, chdir, _run_command):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'diff']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.diff()

        self.assertEqual(2, chdir.call_count)
        _run_command.assert_called_once_with(['git', 'diff'])

    @patch('pyrpkg.Commands._run_command')
    @patch('pyrpkg.os.chdir')
    def test_diff_cached(self, chdir, _run_command):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'diff', '--cached']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.diff()

        self.assertEqual(2, chdir.call_count)
        _run_command.assert_called_once_with(['git', 'diff', '--cached'])


class TestGimmeSpec(CliTestCase):

    @patch('sys.stdout', new=StringIO())
    def test_gimmespec(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'gimmespec']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.gimmespec()

        output = sys.stdout.getvalue().strip()
        self.assertEqual('docpkg.spec', output)


class TestClean(CliTestCase):

    def test_dry_run(self):
        self.make_changes(untracked=True)

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'clean', '--dry-run']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.clean()

        self.assertFilesExist(['new-file.txt'], search_dir=self.cloned_repo_path)

    def test_clean(self):
        self.make_changes(untracked=True)
        dirname = os.path.join(self.cloned_repo_path, 'temp-build')
        os.mkdir(dirname)

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'clean']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.clean()

        self.assertFalse(os.path.exists(os.path.join(self.cloned_repo_path, 'new-file.txt')))
        self.assertFalse(os.path.exists(dirname))

        # Ensure no tracked files and directories are removed.
        self.assertFilesExist(['docpkg.spec', '.git'], search_dir=self.cloned_repo_path)


class TestLint(CliTestCase):

    @patch('pyrpkg.Commands._run_command')
    def test_lint(self, _run_command):
        self.checkout_branch(git.Repo(self.cloned_repo_path), 'eng-rhel-7')

        cli_cmd = ['rpkg', '--name', 'docpkg', '--path', self.cloned_repo_path, 'lint']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.lint()

        rpmlint = ['rpmlint', os.path.join(cli.cmd.path, cli.cmd.spec)]
        _run_command.assert_called_once_with(rpmlint, shell=True)

    @patch('pyrpkg.Commands._run_command')
    def test_lint_warning_with_info(self, _run_command):
        self.checkout_branch(git.Repo(self.cloned_repo_path), 'eng-rhel-7')

        cli_cmd = ['rpkg', '--name', 'docpkg', '--path', self.cloned_repo_path,
                   'lint', '--info']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.lint()

        rpmlint = ['rpmlint', '-i', os.path.join(cli.cmd.path, cli.cmd.spec)]
        _run_command.assert_called_once_with(rpmlint, shell=True)

    @patch('pyrpkg.Commands._run_command')
    def test_lint_with_default_config_file(self, _run_command):
        self.checkout_branch(git.Repo(self.cloned_repo_path), 'eng-rhel-7')

        lint_config_path = os.path.join(self.cloned_repo_path, 'docpkg.rpmlintrc')
        open(lint_config_path, 'a').close()

        cli_cmd = ['rpkg', '--name', 'docpkg', '--path', self.cloned_repo_path, 'lint']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.lint()

        rpmlint = ['rpmlint', '-f', lint_config_path, os.path.join(cli.cmd.path, cli.cmd.spec)]
        _run_command.assert_called_once_with(rpmlint, shell=True)

    @patch('pyrpkg.Commands._run_command')
    def test_lint_with_default_and_deprecated_config_files(self, _run_command):
        self.checkout_branch(git.Repo(self.cloned_repo_path), 'eng-rhel-7')

        lint_config_path = os.path.join(self.cloned_repo_path, 'docpkg.rpmlintrc')
        open(lint_config_path, 'a').close()
        deprecated_lint_config_path = os.path.join(self.cloned_repo_path, '.rpmlint')
        open(deprecated_lint_config_path, 'a').close()

        cli_cmd = ['rpkg', '--name', 'docpkg', '--path', self.cloned_repo_path, 'lint']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.lint()

        rpmlint = ['rpmlint', '-f', lint_config_path, os.path.join(cli.cmd.path, cli.cmd.spec)]
        _run_command.assert_called_once_with(rpmlint, shell=True)

    @patch('pyrpkg.Commands._run_command')
    def test_lint_with_custom_config_file(self, _run_command):
        self.checkout_branch(git.Repo(self.cloned_repo_path), 'eng-rhel-7')

        lint_config_path = os.path.join(self.cloned_repo_path, 'docpkg.rpmlintrc')
        open(lint_config_path, 'a').close()
        custom_lint_config_path = os.path.join(self.cloned_repo_path, 'custom.rpmlintrc')
        open(custom_lint_config_path, 'a').close()

        cli_cmd = ['rpkg', '--name', 'docpkg', '--path', self.cloned_repo_path,
                   'lint', '--rpmlintconf', 'custom.rpmlintrc']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.lint()

        rpmlint = ['rpmlint', '-f', custom_lint_config_path, os.path.join(cli.cmd.path,
                                                                          cli.cmd.spec)]
        _run_command.assert_called_once_with(rpmlint, shell=True)


class TestGitUrl(CliTestCase):

    @patch('sys.stdout', new=StringIO())
    def test_giturl(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'giturl']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.giturl()

        last_commit = str(six.next(cli.cmd.repo.iter_commits()))
        expected_giturl = '{0}#{1}'.format(
            cli.cmd.anongiturl % {'repo': os.path.basename(self.repo_path)},
            last_commit)
        output = sys.stdout.getvalue().strip()
        self.assertEqual(expected_giturl, output)


class TestNew(CliTestCase):

    def test_no_tags_yet(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'new']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            try:
                cli.new()
            except rpkgError as e:
                self.assertTrue('no tags' in str(e))
            else:
                self.fail('Command new should fail due to no tags in the repo.')

    @patch('sys.stdout', new=StringIO())
    def test_get_diff(self):
        self.run_cmd(['git', 'tag', '-m', 'New release v0.1', 'v0.1'],
                     cwd=self.cloned_repo_path,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.make_changes(repo=self.cloned_repo_path,
                          commit=True,
                          content='New change')

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'new']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.new()

            output = sys.stdout.getvalue()
            self.assertTrue('+New change' in output)

    @patch('sys.stdout', new=StringIO())
    @patch('pyrpkg.Commands.new')
    def test_diff_returned_as_bytestring(self, new):
        # diff is return from Commands.new as bytestring when using
        # GitPython<1.0. So, mock new method directly to test diff in
        #  bytestring can be printed correctly.
        new.return_value = 'New content'
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'new']
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.new()

        output = sys.stdout.getvalue()
        self.assertTrue('New content' in output)


class TestNewPrintUnicode(CliTestCase):
    """Test new diff contains unicode characters

    Fix issue 205: https://pagure.io/rpkg/issue/205
    """

    def setUp(self):
        super(TestNewPrintUnicode, self).setUp()
        self.run_cmd(['git', 'tag', '-m', 'New release 0.1', '0.1'],
                     cwd=self.cloned_repo_path,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.make_a_dummy_commit(git.Repo(self.cloned_repo_path),
                                 file_content='Include unicode chars á ř',
                                 commit_message=u'Write unicode to file')

    @patch('sys.stdout', new=StringIO())
    def test_get_diff(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'new']
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.new()

            output = sys.stdout.getvalue()
            self.assertTrue('+Include unicode' in output)


class LookasideCacheMock(object):

    def init_lookaside_cache(self):
        self.lookasidecache_storage = tempfile.mkdtemp('rpkg-tests-lookasidecache-storage-')

    def destroy_lookaside_cache(self):
        shutil.rmtree(self.lookasidecache_storage)

    def lookasidecache_upload(self, repo_name, filepath, hash, offline):
        filename = os.path.basename(filepath)
        storage_filename = os.path.join(self.lookasidecache_storage, filename)
        if self._remote_file_exists(filepath, storage_filename):
            raise AlreadyUploadedError("File already uploaded.")
        with open(storage_filename, 'wb') as fout:
            with open(filepath, 'rb') as fin:
                fout.write(fin.read())

    def _remote_file_exists(self, local_file, remote_file):
        if os.path.isfile(remote_file):
            return filecmp.cmp(local_file, remote_file)
        return False

    def lookasidecache_download(self, name, filename, hash, outfile, hashtype=None, **kwargs):
        with open(outfile, 'w') as f:
            f.write('binary data')

    def hash_file(self, filename):
        md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            content = f.read()
            md5.update(content)
        return md5.hexdigest()

    def assertFilesUploaded(self, filenames):
        assert isinstance(filenames, (tuple, list))
        for filename in filenames:
            self.assertTrue(
                os.path.exists(os.path.join(self.lookasidecache_storage, filename)),
                '{0} is not uploaded. It is not in fake lookaside storage.'.format(filename))


class TestUpload(LookasideCacheMock, CliTestCase):
    """Test command upload"""

    def setUp(self):
        super(TestUpload, self).setUp()

        self.init_lookaside_cache()
        self.sources_file = os.path.join(self.cloned_repo_path, 'sources')
        self.gitignore_file = os.path.join(self.cloned_repo_path, '.gitignore')
        self.readme_patch = os.path.join(self.cloned_repo_path, 'readme.patch')
        self.write_file(self.readme_patch, '+Hello world')

    def tearDown(self):
        self.destroy_lookaside_cache()
        super(TestUpload, self).tearDown()

    def test_upload(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'upload', self.readme_patch]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.lookaside.CGILookasideCache.upload', new=self.lookasidecache_upload):
                cli.upload()

        expected_sources_content = '{0}  readme.patch'.format(self.hash_file(self.readme_patch))
        self.assertEqual(expected_sources_content, self.read_file(self.sources_file).strip())
        self.assertTrue('readme.patch' in self.read_file(self.gitignore_file).strip())

        git_status = cli.cmd.repo.git.status()
        self.assertTrue('Changes not staged for commit:' not in git_status)
        self.assertTrue('Changes to be committed:' in git_status)

    def test_append_to_sources(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'upload', self.readme_patch]
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.lookaside.CGILookasideCache.upload', new=self.lookasidecache_upload):
                cli.upload()

        # git tracked files are not allowed to be uploaded to lookaside cache
        readme_rst = os.path.join(self.cloned_repo_path, 'README.rst')
        self.make_changes(filename=readme_rst, content='# dockpkg', commit=True)

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'upload', readme_rst]
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.lookaside.CGILookasideCache.upload', new=self.lookasidecache_upload):
                six.assertRaisesRegex(
                    self, rpkgError,
                    r'/README.rst.+upload files not tracked by git',
                    cli.upload)

        expected_sources_content = [
            '{0}  {1}'.format(self.hash_file(self.readme_patch),
                              os.path.basename(self.readme_patch)),
            ]
        self.assertEqual(expected_sources_content,
                         self.read_file(self.sources_file).strip().split('\n'))

    def test_upload_file_twice_but_checksum_is_different(self):
        self.write_file(os.path.join(self.cloned_repo_path, 'sources'),
                        content='123456  README.rst')

        readme_rst = os.path.join(self.cloned_repo_path, 'README.rst')
        self.write_file(readme_rst, content='Hello rpkg')

        cli_cmd = [
            'rpkg', '--path', self.cloned_repo_path, 'upload', readme_rst
        ]
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.lookaside.CGILookasideCache.upload',
                       new=self.lookasidecache_upload):
                six.assertRaisesRegex(
                    self, rpkgError,
                    r'.+README.rst which has different checksum.+',
                    cli.upload)

    @patch('pyrpkg.log.info')
    def test_upload_file_twice(self, log_info):
        cli_cmd = [
            'rpkg', '--path', self.cloned_repo_path, 'upload', self.readme_patch
        ]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.lookaside.CGILookasideCache.upload',
                       new=self.lookasidecache_upload):
                cli.upload()
                cli.upload()

        self.assertEqual(2, log_info.call_count)
        log_info.assert_has_calls([
            call("Source upload succeeded. Don't forget to commit the sources file"),
            call("All sources were already uploaded."),
        ])


class TestSources(LookasideCacheMock, CliTestCase):

    def setUp(self):
        super(TestSources, self).setUp()
        self.init_lookaside_cache()

        # Uploading a file aims to run the loop in sources command.
        self.readme_patch = os.path.join(self.cloned_repo_path, 'readme.patch')
        self.write_file(self.readme_patch, content='+Welcome to README')

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'upload', self.readme_patch]
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.lookaside.CGILookasideCache.upload', new=self.lookasidecache_upload):
                cli.upload()

    def tearDown(self):
        # Tests may put a file readme.patch in current directory, so, let's remove it.
        if os.path.exists('readme.patch'):
            os.remove('readme.patch')
        self.destroy_lookaside_cache()
        super(TestSources, self).tearDown()

    def test_sources(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'sources']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.lookaside.CGILookasideCache.download',
                       new=self.lookasidecache_download):
                cli.sources()

        # NOTE: without --outdir, whatever to run sources command in package
        # repository, sources file is downloaded into current working
        # directory. Is this a bug, or need to improve?
        self.assertTrue(os.path.exists('readme.patch'))

    def test_sources_to_outdir(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'sources', '--outdir', self.cloned_repo_path]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.lookaside.CGILookasideCache.download',
                       new=self.lookasidecache_download):
                cli.sources()

        self.assertFilesExist(['readme.patch'], search_dir=self.cloned_repo_path)


class TestFailureImportSrpm(CliTestCase):

    def test_import_nonexistent_srpm(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'import', 'nonexistent-srpm']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            try:
                cli.import_srpm()
            except rpkgError as e:
                self.assertEqual('File not found.', str(e))
            else:
                self.fail('import_srpm should fail if srpm does not exist.')

    def test_repo_is_dirty(self):
        srpm_file = os.path.join(os.path.dirname(__file__), 'fixtures', 'docpkg-0.2-1.src.rpm')
        self.make_changes()
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'import', srpm_file]
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            try:
                cli.import_srpm()
            except rpkgError as e:
                self.assertEqual('There are uncommitted changes in your repo', str(e))
            else:
                self.fail('import_srpm should fail if package repository is dirty.')


class TestImportSrpm(LookasideCacheMock, CliTestCase):

    @staticmethod
    def build_srpm(srcrpmdir):
        """Build a fake SRPM used by this test case"""
        docpkg_dir = os.path.join(fixtures_dir, 'docpkg')
        specfile = os.path.join(docpkg_dir, 'docpkg.spec')
        rpmbuild = [
            'rpmbuild', '-bs',
            '--define', '_topdir {0}'.format(srcrpmdir),
            '--define', '_builddir {0}'.format(srcrpmdir),
            '--define', '_sourcedir {0}'.format(docpkg_dir),
            '--define', '_specdir {0}'.format(docpkg_dir),
            specfile
        ]
        proc = subprocess.Popen(
            rpmbuild, stdout=subprocess.PIPE, universal_newlines=True)
        stdout, _ = proc.communicate()
        if proc.returncode > 0:
            raise rpkgError('Failed to build SRPM for test case {0}'.format(
                TestImportSrpm.__name__))
        filename = stdout.splitlines()[-1].split()[-1]
        return filename.strip()

    def setUp(self):
        super(TestImportSrpm, self).setUp()
        self.write_file(os.path.join(self.cloned_repo_path, 'README.md'),
                        content='Cool package')
        self.init_lookaside_cache()

        self.srcrpmdir = tempfile.mkdtemp(prefix='test-import-srpm-topdir-')
        self.srpm_file = TestImportSrpm.build_srpm(self.srcrpmdir)

        self.chaos_repo = tempfile.mkdtemp(prefix='rpkg-tests-chaos-repo-')
        cmds = (
            ['git', 'init'],
            ['git', 'checkout', '-b', 'master'],
            ['touch', 'README.md'],
            ['git', 'add', 'README.md'],
            ['git', 'config', 'user.name', 'tester'],
            ['git', 'config', 'user.email', 'tester@example.com'],
            ['git', 'commit', '-m', '"Add README"'],
        )
        for cmd in cmds:
            self.run_cmd(cmd, cwd=self.chaos_repo,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def tearDown(self):
        shutil.rmtree(self.srcrpmdir)
        shutil.rmtree(self.chaos_repo)
        self.destroy_lookaside_cache()
        super(TestImportSrpm, self).tearDown()

    def assert_import_srpm(self, target_repo):
        cli_cmd = ['rpkg', '--path', target_repo, '--name', 'docpkg',
                   'import', '--skip-diffs', self.srpm_file]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.lookaside.CGILookasideCache.upload', self.lookasidecache_upload):
                cli.import_srpm()

        docpkg_gz = 'docpkg.tar.gz'
        source_without_extension = 'source-without-extension'
        diff_cached = cli.cmd.repo.git.diff('--cached')
        self.assertTrue('+- - New release 0.2-1' in diff_cached)
        self.assertTrue('+hello world' in diff_cached)
        self.assertFilesExist(['.gitignore',
                               'sources',
                               'docpkg.spec',
                               'hello-world.txt',
                               docpkg_gz,
                               source_without_extension,
                               'README.md'], search_dir=target_repo)
        self.assertFilesNotExist(['CHANGELOG.rst'], search_dir=target_repo)
        with open(os.path.join(target_repo, 'sources'), 'r') as f:
            self.assertEqual(
                '{0}  {1}\n{2}  {3}'.format(
                    self.hash_file(os.path.join(target_repo, docpkg_gz)),
                    docpkg_gz,
                    self.hash_file(os.path.join(target_repo, source_without_extension)),
                    source_without_extension,
                ),
                f.read().strip()
            )
        with open(os.path.join(target_repo, '.gitignore'), 'r') as f:
            self.assertEqual(
                '/{0}\n/{1}'.format(docpkg_gz, source_without_extension),
                f.read().strip()
            )
        self.assertFilesUploaded([docpkg_gz, source_without_extension])

    def test_import(self):
        self.assert_import_srpm(self.chaos_repo)
        # Exception is not a functionality issue. There is no problem with
        # uploading same file twice in a test however, the upload method checks
        # if file has been already uploaded.
        self.assertRaisesRegex(AlreadyUploadedError, r'File already uploaded',
                               self.assert_import_srpm, self.cloned_repo_path)

    def test_import_gating_and_rpmlintrc_exception(self):
        # Add three additional files to the repo. Former gating.yaml and package.rpmlintrc are
        # listed among reserved files, latter is not and after import it should
        # be removed from the repo.
        cmds = (
            ['touch', 'gating.yaml'],
            ['touch', 'package.rpmlintrc'],
            ['touch', 'the_file_is_not_in_reserved.yaml'],
            ['git', 'add', 'gating.yaml'],
            ['git', 'add', 'package.rpmlintrc'],
            ['git', 'add', 'the_file_is_not_in_reserved.yaml'],
            ['git', 'commit', '--amend', '--no-edit'],  # non-interactive amend
        )
        for cmd in cmds:
            self.run_cmd(cmd, cwd=self.chaos_repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        cli_cmd = ['rpkg', '--path', self.chaos_repo, '--name', 'docpkg',
                   'import', '--skip-diffs', self.srpm_file]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.lookaside.CGILookasideCache.upload', self.lookasidecache_upload):
                cli.import_srpm()

        self.assertFilesExist(['gating.yaml'], search_dir=self.chaos_repo)
        self.assertFilesExist(['package.rpmlintrc'], search_dir=self.chaos_repo)
        self.assertFilesNotExist(['the_file_is_not_in_reserved.yaml'], search_dir=self.chaos_repo)


class TestMockbuild(CliTestCase):
    """Test mockbuild command"""

    create_repo_per_test = False

    def setUp(self):
        super(TestMockbuild, self).setUp()
        self.run_command_patcher = patch('pyrpkg.Commands._run_command')
        self.mock_run_command = self.run_command_patcher.start()

    def tearDown(self):
        self.run_command_patcher.stop()
        super(TestMockbuild, self).tearDown()

    def mockbuild(self, cli_cmd):
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.mockbuild()
            return cli

    def test_mockbuild(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   '--release', 'rhel-6', 'mockbuild',
                   '--root', '/etc/mock/some-root',
                   '--enablerepo', 'FAVOURITE_REPO', '--disablerepo', 'UNWANTED_REPO',
                   '--enablerepo', 'ANOTHER_FAVOURITE_REPO',
                   '--enable-network']
        cli = self.mockbuild(cli_cmd)

        expected_cmd = ['mock', '--enablerepo', 'FAVOURITE_REPO',
                        '--enablerepo', 'ANOTHER_FAVOURITE_REPO',
                        '--disablerepo', 'UNWANTED_REPO',
                        '--enable-network',
                        '-r', '/etc/mock/some-root',
                        '--resultdir', cli.cmd.mock_results_dir, '--rebuild',
                        cli.cmd.srpmname]
        self.mock_run_command.assert_called_with(expected_cmd)

    def test_with_without(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   '--release', 'rhel-6', 'mockbuild',
                   '--root', '/etc/mock/some-root',
                   '--with', 'a', '--without', 'b', '--with', 'c',
                   '--without', 'd']
        cli = self.mockbuild(cli_cmd)

        expected_cmd = ['mock', '--with', 'a', '--with', 'c',
                        '--without', 'b', '--without', 'd',
                        '-r', '/etc/mock/some-root',
                        '--resultdir', cli.cmd.mock_results_dir, '--rebuild',
                        cli.cmd.srpmname]
        self.mock_run_command.assert_called_with(expected_cmd)

    @patch('pyrpkg.Commands._config_dir_basic')
    @patch('pyrpkg.Commands._config_dir_other')
    @patch('os.path.exists', return_value=False)
    def test_use_mock_config_got_from_koji(
            self, exists, config_dir_other, config_dir_basic):
        mock_layout = layout.DistGitLayout(root_dir=self.cloned_repo_path)
        with patch('pyrpkg.layout.build', return_value=mock_layout):
            config_dir_basic.return_value = '/path/to/config-dir'

            cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                       '--release', 'rhel-7', 'mockbuild']
            self.mockbuild(cli_cmd)

        args, kwargs = self.mock_run_command.call_args
        cmd_to_execute = args[0]

        self.assertTrue('--configdir' in cmd_to_execute)
        self.assertTrue(config_dir_basic.return_value in cmd_to_execute)

    @patch('pyrpkg.Commands._config_dir_basic')
    @patch('os.path.exists', return_value=False)
    def test_fail_to_store_mock_config_in_created_config_dir(
            self, exists, config_dir_basic):
        config_dir_basic.side_effect = rpkgError

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   '--release', 'rhel-7', 'mockbuild']
        self.assertRaises(rpkgError, self.mockbuild, cli_cmd)

    @patch('pyrpkg.Commands._config_dir_basic')
    @patch('pyrpkg.Commands._config_dir_other')
    @patch('os.path.exists', return_value=False)
    def test_fail_to_populate_mock_config(
            self, exists, config_dir_other, config_dir_basic):
        config_dir_basic.return_value = '/path/to/config-dir'
        config_dir_other.side_effect = rpkgError

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   '--release', 'rhel-7', 'mockbuild']
        self.assertRaises(rpkgError, self.mockbuild, cli_cmd)

    def test_shell_option(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   '--release', 'rhel-6', 'mockbuild',
                   '--root', '/etc/mock/some-root', '--shell']
        cli = self.mockbuild(cli_cmd)

        expected_cmd = [
            'mock', '-r', '/etc/mock/some-root',
            '--resultdir', cli.cmd.mock_results_dir, '--shell'
        ]
        self.mock_run_command.assert_called_with(expected_cmd)

    def test_extra_args(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   '--release', 'rhel-6', 'mockbuild',
                   '--root', '/etc/mock/some-root',
                   '--with', 'a',
                   '--', '--with', 'd', '--without', '"bb"']
        cli = self.mockbuild(cli_cmd)

        expected_cmd = ['mock', '--with', 'a', '--with', 'd',
                        '--without', '"bb"', '-r', '/etc/mock/some-root',
                        '--resultdir', cli.cmd.mock_results_dir, '--rebuild',
                        cli.cmd.srpmname]
        self.mock_run_command.assert_called_with(expected_cmd)

    def test_extra_args_new_arguments(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   '--release', 'rhel-6', 'mockbuild',
                   '--root', '/etc/mock/some-root',
                   '--', '--nocheck', '--arch=amd64', '-q']
        cli = self.mockbuild(cli_cmd)

        expected_cmd = ['mock', '--nocheck', '--arch=amd64', '-q',
                        '-r', '/etc/mock/some-root',
                        '--resultdir', cli.cmd.mock_results_dir, '--rebuild',
                        cli.cmd.srpmname]
        self.mock_run_command.assert_called_with(expected_cmd)


class TestCoprBuild(CliTestCase):
    """Test copr command"""

    create_repo_per_test = False

    def setUp(self):
        super(TestCoprBuild, self).setUp()
        self.nvr_patcher = patch('pyrpkg.Commands.nvr',
                                 new_callable=PropertyMock,
                                 return_value='rpkg-1.29-3.fc26')
        self.mock_nvr = self.nvr_patcher.start()

        self.srpm_patcher = patch('pyrpkg.cli.cliClient.srpm')
        self.mock_srpm = self.srpm_patcher.start()

        self.run_command_patcher = patch('pyrpkg.Commands._run_command')
        self.mock_run_command = self.run_command_patcher.start()

    def tearDown(self):
        self.run_command_patcher.stop()
        self.srpm_patcher.stop()
        self.nvr_patcher.stop()
        super(TestCoprBuild, self).tearDown()

    def assert_copr_build(self, cli_cmd, expected_copr_cli):
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.copr_build()

        self.mock_srpm.assert_called_once()
        self.mock_run_command.assert_called_once_with(expected_copr_cli)

    def test_copr_build(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'copr-build', 'user/project']

        self.assert_copr_build(cli_cmd, [
            'copr-cli', 'build', 'user/project',
            '{0}.src.rpm'.format(self.mock_nvr.return_value)
        ])

    def test_copr_build_no_wait(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'copr-build', '--nowait', 'user/project']

        self.assert_copr_build(cli_cmd, [
            'copr-cli', 'build', '--nowait', 'user/project',
            '{0}.src.rpm'.format(self.mock_nvr.return_value)
        ])

    def test_copr_build_with_alternative_config_file(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'copr-build', '--config', '/path/to/alternative/config',
                   'user/project']

        self.assert_copr_build(cli_cmd, [
            'copr-cli', '--config', '/path/to/alternative/config',
            'build', 'user/project',
            '{0}.src.rpm'.format(self.mock_nvr.return_value)
        ])


class TestMockConfig(CliTestCase):
    """Test mockconfig command"""

    create_repo_per_test = False

    def setUp(self):
        super(TestMockConfig, self).setUp()

        self.topurl_patcher = patch('pyrpkg.Commands.topurl',
                                    new_callable=PropertyMock,
                                    return_value='http://localhost/hub')
        self.mock_topurl = self.topurl_patcher.start()

        self.disttag_patcher = patch('pyrpkg.Commands.disttag',
                                     new_callable=PropertyMock,
                                     return_value='fc26')
        self.mock_disttag = self.disttag_patcher.start()

        self.target_patcher = patch('pyrpkg.Commands.target',
                                    new_callable=PropertyMock,
                                    return_value='f26-candidate')
        self.mock_target = self.target_patcher.start()

        self.localarch_patcher = patch('pyrpkg.Commands.localarch',
                                       new_callable=PropertyMock,
                                       return_value='x86_64')
        self.mock_localarch = self.localarch_patcher.start()

        self.genMockConfig_patcher = patch('koji.genMockConfig',
                                           return_value='x86_64 mock config')
        self.mock_genMockConfig = self.genMockConfig_patcher.start()

        self.fake_build_target = {
            'build_tag': 364,
            'build_tag_name': 'f26-build',
            'dest_tag': 359,
            'dest_tag_name': 'f26-updates-candidate',
            'id': 178,
            'name': 'f26-candidate'
        }
        self.fake_repo = {
            'create_event': 27478349,
            'create_ts': 1506694416.4495,
            'creation_time': '2017-09-29 14:13:36.449504',
            'dist': False,
            'id': 790843,
            'state': 1
        }

        self.anon_kojisession_patcher = patch(
            'pyrpkg.Commands.anon_kojisession',
            new_callable=PropertyMock)
        self.mock_anon_kojisession = self.anon_kojisession_patcher.start()
        self.kojisession = self.mock_anon_kojisession.return_value
        self.kojisession.getBuildTarget.return_value = self.fake_build_target
        self.kojisession.getRepo.return_value = self.fake_repo
        self.kojisession.getBuildConfig.return_value = {
            "extra": {"mock.package_manager": "dnf", "mock.yum.module_hotfixes": 1}
        }

    def tearDown(self):
        self.genMockConfig_patcher.stop()
        self.localarch_patcher.stop()
        self.target_patcher.stop()
        self.disttag_patcher.stop()
        self.topurl_patcher.stop()
        super(TestMockConfig, self).tearDown()

    @patch('sys.stdout', new_callable=StringIO)
    def test_mock_config(self, stdout):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'mock-config']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.mock_config()

        self.mock_genMockConfig.assert_called_once_with(
            'f26-candidate-x86_64',
            'x86_64',
            distribution='fc26',
            tag_name=self.fake_build_target['build_tag_name'],
            repoid=self.fake_repo['id'],
            topurl='http://localhost/hub',
            package_manager="dnf",
            module_hotfixes=1,
        )

        mock_config = stdout.getvalue().strip()
        self.assertEqual('x86_64 mock config', mock_config)

    def test_fail_if_specified_target_not_exists(self):
        self.kojisession.getBuildTarget.return_value = None

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'mock-config', '--target', 'some-target']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            self.assertRaises(rpkgError, cli.mock_config)

    def test_fail_if_cannot_find_a_valid_repo(self):
        self.kojisession.getRepo.side_effect = Exception

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'mock-config']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            self.assertRaises(rpkgError, cli.mock_config)

    def test_mock_config_from_specified_target(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'mock-config', '--target', 'f25-candidate']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.mock_config()

        self.kojisession.getBuildTarget.assert_called_once_with(
            'f25-candidate')
        args, kwargs = self.mock_genMockConfig.call_args
        self.assertEqual('f25-candidate-x86_64', args[0])

    def test_mock_config_from_specified_arch(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'mock-config', '--arch', 'i686']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.mock_config()

        args, kwargs = self.mock_genMockConfig.call_args
        self.assertEqual('f26-candidate-i686', args[0])
        self.assertEqual('i686', args[1])


class TestContainerBuildSetup(CliTestCase):
    """Test container-build-setup command"""

    def setUp(self):
        super(TestContainerBuildSetup, self).setUp()

        self.osbs_repo_config = os.path.join(self.cloned_repo_path,
                                             '.osbs-repo-config')
        self.write_file(self.osbs_repo_config, '''[autorebuild]
enabled = True
''')

        self.log_patcher = patch.object(pyrpkg, 'log')
        self.mock_log = self.log_patcher.start()

    def tearDown(self):
        if os.path.exists(self.osbs_repo_config):
            os.unlink(self.osbs_repo_config)
        self.log_patcher.stop()
        super(TestContainerBuildSetup, self).tearDown()

    def test_get_autorebuild_when_config_file_not_exists(self):
        os.unlink(self.osbs_repo_config)

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'container-build-setup', '--get-autorebuild']
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.container_build_setup()

        self.mock_log.info.assert_called_once_with('false')

    def test_get_autorebuild_from_config_file(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'container-build-setup', '--get-autorebuild']
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.container_build_setup()

        self.mock_log.info.assert_called_once_with('true')

    def test_set_autorebuild_by_creating_config_file(self):
        os.unlink(self.osbs_repo_config)

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'container-build-setup', '--set-autorebuild', 'true']
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.Commands.repo',
                       new_callable=PropertyMock) as repo:
                cli.container_build_setup()

                repo.return_value.index.add.assert_called_once_with(
                    [self.osbs_repo_config])

        repo_config = self.read_file(self.osbs_repo_config).strip()
        self.assertEqual('''[autorebuild]
enabled = true''', repo_config)

    def test_set_autorebuild_in_existing_config_file(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'container-build-setup', '--set-autorebuild', 'false']
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch('pyrpkg.Commands.repo',
                       new_callable=PropertyMock) as repo:
                cli.container_build_setup()

                repo.return_value.index.add.assert_called_once_with(
                    [self.osbs_repo_config])

        repo_config = self.read_file(self.osbs_repo_config).strip()
        self.assertEqual('''[autorebuild]
enabled = false''', repo_config)


class TestPatch(CliTestCase):
    """Test patch command"""

    create_repo_per_test = False

    def setUp(self):
        super(TestPatch, self).setUp()

        self.repo_patcher = patch('pyrpkg.Commands.repo',
                                  new_callable=PropertyMock)
        self.mock_repo = self.repo_patcher.start()

        self.Popen_patcher = patch('subprocess.Popen')
        self.mock_Popen = self.Popen_patcher.start()

        self.repo_name_patcher = patch('pyrpkg.Commands.repo_name',
                                       new_callable=PropertyMock,
                                       return_value='docpkg')
        self.mock_repo_name = self.repo_name_patcher.start()

        self.ver_patcher = patch('pyrpkg.Commands.ver',
                                 new_callable=PropertyMock,
                                 return_value='2.0')
        self.mock_ver = self.ver_patcher.start()

    def tearDown(self):
        self.ver_patcher.stop()
        self.repo_name_patcher.stop()
        self.Popen_patcher.stop()
        self.repo_patcher.stop()
        super(TestPatch, self).tearDown()

    def test_expanded_source_dir_not_found(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'patch', 'fix']

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            six.assertRaisesRegex(
                self, rpkgError,
                'Expanded source dir not found!', cli.patch)

    @patch('os.path.isdir', return_value=True)
    def test_generate_diff(self, isdir):
        self.mock_Popen.return_value.communicate.return_value = ['+ diff', '']

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'patch', 'fix']
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with patch.object(six.moves.builtins, 'open', mock_open()) as m:
                cli.patch()
                m.return_value.write.assert_called_once_with('+ diff')

        patch_file = '{0}-{1}-fix.patch'.format(cli.cmd.repo_name,
                                                cli.cmd.ver)
        self.mock_repo.return_value.index.add.assert_called_once_with(
                [patch_file])

    @patch('os.path.isdir', return_value=True)
    def test_generate_empty_patch(self, isdir):
        self.mock_Popen.return_value.communicate.return_value = ['', '']

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path, 'patch', 'fix']
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            six.assertRaisesRegex(
                self, rpkgError,
                'gendiff generated an empty patch!', cli.patch)

    @patch('os.rename')
    @patch('os.path.isdir', return_value=True)
    def test_rediff(self, isdir, rename):
        origin_diff = '''diff -up fedpkg-1.29/fedpkg/__init__.py.origin fedpkg-1.29/fedpkg/__init__.py
--- fedpkg-1.29/fedpkg/__init__.py.origin  2017-10-05 01:55:34.268488598 +0000
+++ fedpkg-1.29/fedpkg/__init__.py	2017-10-05 01:55:59.736947877 +0000
@@ -9,12 +9,12 @@
 # option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
 # the full text of the license.

-import pyrpkg'''

        self.mock_Popen.return_value.communicate.return_value = [
            origin_diff, '']

        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'patch', '--rediff', 'fix']
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()

            patch_file = '{0}-{1}-fix.patch'.format(cli.cmd.repo_name,
                                                    cli.cmd.ver)
            copied_patch_file = '{0}~'.format(patch_file)

            with patch.object(six.moves.builtins, 'open',
                              mock_open(read_data=origin_diff)) as m:
                with patch('os.path.exists', return_value=True) as exists:
                    cli.patch()

                    exists.assert_called_once_with(
                        os.path.join(cli.cmd.path, patch_file))

                rename.assert_called_once_with(
                    os.path.join(cli.cmd.path, patch_file),
                    os.path.join(cli.cmd.path, copied_patch_file))

                # Following calls assert_has_calls twice in order is a
                # workaround for running this test with old mock 1.0.1, that
                # is the latest version in el6 and el7.
                #
                # When run this test with newer version of mock, e.g. 2.0.0,
                # these 4 calls can be asserted together in order in a single
                # call of m.assert_has_calls.
                m.assert_has_calls([
                    call(os.path.join(cli.cmd.path, patch_file), 'r'),
                    call().readlines(),
                ])
                # Here, skip to check call().readlines().__iter__() that
                # happens only within mock 1.0.1.
                m.assert_has_calls([
                    call(os.path.join(cli.cmd.path, patch_file), 'w'),
                    call().write(origin_diff),
                ])

    def test_fail_if_no_previous_diff_exists(self):
        cli_cmd = ['rpkg', '--path', self.cloned_repo_path,
                   'patch', '--rediff', 'fix']
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()

            patch_file = '{0}-{1}-fix.patch'.format(cli.cmd.repo_name,
                                                    cli.cmd.ver)
            with patch('os.path.exists', return_value=False) as exists:
                six.assertRaisesRegex(
                    self, rpkgError,
                    'Patch file [^ ]+ not found, unable to rediff', cli.patch)

                exists.assert_called_once_with(
                    os.path.join(cli.cmd.path, patch_file))


class FakeKojiCreds(object):

    @classmethod
    def setUpClass(cls):
        super(FakeKojiCreds, cls).setUpClass()

        fake_koji_config = dict(
            authtype='kerberos',
            server='http://localhost/kojihub',
            weburl='http://localhost/koji',
            topurl='http://kojipkgs.localhost/',
            cert='',
        )
        cls.read_config_p = patch('koji.read_config',
                                  return_value=fake_koji_config)
        cls.mock_read_config = cls.read_config_p.start()
        cls.load_krb_user_p = patch('pyrpkg.Commands._load_krb_user')
        cls.mock_load_krb_user = cls.load_krb_user_p.start()

        cls.has_krb_creds_p = patch('pyrpkg.Commands._has_krb_creds',
                                    return_value=True)
        cls.mock_has_krb_creds = cls.has_krb_creds_p.start()

    @classmethod
    def tearDownClass(cls):
        cls.has_krb_creds_p.stop()
        cls.load_krb_user_p.stop()
        cls.read_config_p.stop()
        super(FakeKojiCreds, cls).tearDownClass()

    def setUp(self):
        super(FakeKojiCreds, self).setUp()

        self.ClientSession_p = patch('koji.ClientSession')
        self.mock_ClientSession = self.ClientSession_p.start()

    def tearDown(self):
        self.ClientSession_p.stop()
        super(FakeKojiCreds, self).tearDown()


@unittest.skipUnless(
    openidc_client,
    'Skip if rpkg is rebuilt for an environment where Kerberos authentication'
    'is used and python-openidc-client is not available.')
class TestModulesCli(FakeKojiCreds, CliTestCase):
    """Test module commands"""

    create_repo_per_test = False

    scopes = [
        'openid',
        'https://id.fedoraproject.org/scope/groups',
        'https://mbs.fedoraproject.org/oidc/submit-build'
    ]
    module_build_json = {
        'component_builds': [
            59417, 59418, 59419, 59420, 59421, 59422, 59423, 59428,
            59424, 59425],
        'id': 2150,
        'koji_tag': 'module-14050f52e62d955b',
        'modulemd': '...',
        'name': 'python3-ecosystem',
        'owner': 'torsava',
        'scmurl': ('git://pkgs.fedoraproject.org/modules/python3-ecosystem'
                    '?#34774a9416c799aadda74f2c44ec4dba4d519c04'),
        'state': 4,
        'state_name': 'failed',
        'state_reason': 'Some error',
        'state_trace': [],
        'state_url': '/module-build-service/1/module-builds/1093',
        'stream': 'master',
        'tasks': {
            'rpms': {
                'module-build-macros': {
                    'nvr': 'module-build-macros-None-None',
                    'state': 3,
                    'state_reason': 'Some error',
                    'task_id': 22370514
                },
                'python-cryptography': {
                    'nvr': None,
                    'state': 3,
                    'state_reason': 'Some error',
                    'task_id': None
                },
                'python-dns': {
                    'nvr': None,
                    'state': 3,
                    'state_reason': 'Some error',
                    'task_id': None
                }
            }
        },
        'time_completed': '2017-10-11T09:42:11Z',
        'time_modified': '2017-10-11T09:42:11Z',
        'time_submitted': '2017-10-10T14:55:33Z',
        'version': '20171010145511'
    }

    @classmethod
    def setUpClass(cls):
        super(TestModulesCli, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestModulesCli, cls).tearDownClass()

    def setUp(self):
        super(TestModulesCli, self).setUp()

    def tearDown(self):
        super(TestModulesCli, self).tearDown()

        # Test may generate yaml file for itself to run the test.
        # Clean it for next test to run.
        files_pattern = os.path.join(self.cloned_repo_path, '*.yaml')
        for filename in glob.glob(files_pattern):
            os.unlink(filename)

    @patch('sys.stdout', new=StringIO())
    @patch('requests.get')
    @patch('openidc_client.OpenIDCClient.send_request')
    def test_module_build_v1(self, mock_oidc_req, mock_get):
        """
        Test a module build with an SCM URL and branch supplied
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build',
            'git://pkgs.fedoraproject.org/modules/testmodule?#79d87a5a',
            'master'
        ]
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 1
        }
        mock_oidc_req.return_value.json.return_value = {'id': 1094}

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.module_build()

        mock_get.assert_called_once_with(
            'https://mbs.fedoraproject.org/module-build-service/1/about/',
            timeout=60
        )
        exp_url = ('https://mbs.fedoraproject.org/module-build-service/1/'
                   'module-builds/')
        exp_json = {
            'scmurl': ('git://pkgs.fedoraproject.org/modules/testmodule?'
                       '#79d87a5a'),
            'branch': 'master',
            'scratch': False,
            }
        mock_oidc_req.assert_called_once_with(
            exp_url,
            http_method='POST',
            json=exp_json,
            scopes=self.scopes,
            timeout=120)
        output = sys.stdout.getvalue().strip()
        expected_output = (
            'Submitting the module build...',
            'The build 1094 was submitted to the MBS',
            'Build URLs:',
            cli.cmd.module_get_url(1094, verbose=False),
        )
        self.assertEqual(output, '\n'.join(expected_output))

    @patch('sys.stdout', new=StringIO())
    @patch('requests.get')
    @patch('openidc_client.OpenIDCClient.send_request')
    def test_module_build_v2(self, mock_oidc_req, mock_get):
        """
        Test a module build with an SCM URL and branch supplied on the v2 API
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build',
            'git://pkgs.fedoraproject.org/modules/testmodule?#79d87a5a',
            'master'
        ]
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }
        mock_oidc_req.return_value.json.return_value = [
            {'id': 1094}, {'id': 1095}, {'id': 1096}]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.module_build()

        mock_get.assert_called_once_with(
            'https://mbs.fedoraproject.org/module-build-service/1/about/',
            timeout=60
        )
        exp_url = ('https://mbs.fedoraproject.org/module-build-service/2/'
                   'module-builds/')
        exp_json = {
            'scmurl': ('git://pkgs.fedoraproject.org/modules/testmodule?'
                       '#79d87a5a'),
            'branch': 'master',
            'scratch': False,
            }
        mock_oidc_req.assert_called_once_with(
            exp_url,
            http_method='POST',
            json=exp_json,
            scopes=self.scopes,
            timeout=120)
        output = sys.stdout.getvalue().strip()
        expected_output = (
            'Submitting the module build...',
            'The builds 1094, 1095 and 1096 were submitted to the MBS',
            'Build URLs:',
            cli.cmd.module_get_url(1094, verbose=False),
            cli.cmd.module_get_url(1095, verbose=False),
            cli.cmd.module_get_url(1096, verbose=False),
        )
        self.assertEqual(output, '\n'.join(expected_output))

    @patch('requests.get')
    @patch('openidc_client.OpenIDCClient.send_request')
    def test_module_build_dep_overrides(self, mock_oidc_req, mock_get):
        """
        Test a module build with buildrequire and require overrides
        """
        cli_cmd = [
            'rpkg',
            '--path', self.cloned_repo_path,
            'module-build',
            'git://pkgs.fedoraproject.org/modules/testmodule?#79d87a5a',
            'master',
            '--buildrequires', 'platform:f28',
            '--buildrequires', 'platform:f29',
            '--requires', 'platform:f29'
        ]
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }
        mock_oidc_req.return_value.json.return_value = [
            {'id': 1094}, {'id': 1095}, {'id': 1096}]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.module_build()

        brs = mock_oidc_req.call_args[1]['json']['buildrequire_overrides']
        assert set(brs['platform']) == set(['f28', 'f29'])
        reqs = mock_oidc_req.call_args[1]['json']['require_overrides']
        assert reqs['platform'] == ['f29']

    @patch('sys.stderr', new_callable=StringIO)
    def test_module_build_conflicting_keys(self, stderr):
        """
        Test a module build with optional arguments that conflict with other arguments
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build',
            'git://pkgs.fedoraproject.org/modules/testmodule?#79d87a5a',
            'master',
            '--optional', 'scmurl=git://pkgs.fedoraproject.org/modules/testmodule?#1234'
        ]

        with patch('sys.argv', new=cli_cmd):
            with self.assertRaises(SystemExit) as cm:
                self.new_cli()

        assert stderr.getvalue().strip().endswith(
            'The "scmurl" optional argument is reserved to built-in arguments')
        assert cm.exception.code == 2

    @patch('sys.stdout', new=StringIO())
    @patch('requests.get')
    @patch('openidc_client.OpenIDCClient.send_request')
    def test_module_build_input(self, mock_oidc_req, mock_get):
        """
        Test a module build with default parameters
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build'
        ]
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }
        mock_oidc_req.return_value.json.return_value = [{'id': 1094}]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.module_build()

        output = sys.stdout.getvalue().strip()
        expected_output = (
            'Submitting the module build...',
            'The build 1094 was submitted to the MBS',
            'Build URLs:',
            cli.cmd.module_get_url(1094, verbose=False)
        )
        self.assertEqual(output, '\n'.join(expected_output))
        mock_get.assert_called_once_with(
            'https://mbs.fedoraproject.org/module-build-service/1/about/',
            timeout=60
        )
        exp_url = ('https://mbs.fedoraproject.org/module-build-service/2/'
                   'module-builds/')
        exp_json = {
            'scmurl': ANY,
            'branch': 'master',
            'scratch': False,
            }
        mock_oidc_req.assert_called_once_with(
            exp_url,
            http_method='POST',
            json=exp_json,
            scopes=self.scopes,
            timeout=120)

    @patch('sys.stdout', new=StringIO())
    @patch('requests.get')
    @patch('openidc_client.OpenIDCClient.send_request')
    def test_module_build_scratch(self, mock_oidc_req, mock_get):
        """
        Test a scratch module build with default parameters
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-scratch-build',
        ]
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }
        mock_oidc_req.return_value.json.return_value = [{'id': 1094}]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.module_scratch_build()

        output = sys.stdout.getvalue().strip()
        expected_output = (
            'Submitting the module build...',
            'The build 1094 was submitted to the MBS',
            'Build URLs:',
            cli.cmd.module_get_url(1094, verbose=False),
        )
        self.assertEqual(output, '\n'.join(expected_output))
        mock_get.assert_called_once_with(
            'https://mbs.fedoraproject.org/module-build-service/1/about/',
            timeout=60
        )
        exp_url = ('https://mbs.fedoraproject.org/module-build-service/2/'
                   'module-builds/')
        exp_json = {
            'scmurl': ANY,
            'branch': 'master',
            'scratch': True,
            }
        mock_oidc_req.assert_called_once_with(
            exp_url,
            http_method='POST',
            json=exp_json,
            scopes=self.scopes,
            timeout=120)

    @patch('sys.stdout', new=StringIO())
    @patch('requests.get')
    @patch('openidc_client.OpenIDCClient.send_request')
    def test_module_build_with_scratch_option(self, mock_oidc_req, mock_get):
        """
        Test a scratch module build with default parameters using scratch option
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build',
            '--scratch'
        ]
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }
        mock_oidc_req.return_value.json.return_value = [{'id': 1094}]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.module_build()

        output = sys.stdout.getvalue().strip()
        expected_output = (
            'Submitting the module build...',
            'The build 1094 was submitted to the MBS',
            'Build URLs:',
            cli.cmd.module_get_url(1094, verbose=False),
        )
        self.assertEqual(output, '\n'.join(expected_output))
        mock_get.assert_called_once_with(
            'https://mbs.fedoraproject.org/module-build-service/1/about/',
            timeout=60
        )
        exp_url = ('https://mbs.fedoraproject.org/module-build-service/2/'
                   'module-builds/')
        exp_json = {
            'scmurl': ANY,
            'branch': 'master',
            'scratch': True,
            }
        mock_oidc_req.assert_called_once_with(
            exp_url,
            http_method='POST',
            json=exp_json,
            scopes=self.scopes,
            timeout=120)

    @patch('sys.stdout', new=StringIO())
    @patch('pyrpkg.cli.cliClient._get_rpm_package_name', new=mock_get_rpm_package_name)
    @patch('requests.get')
    @patch('openidc_client.OpenIDCClient.send_request')
    def test_module_build_scratch_with_modulemd_and_srpms(self, mock_oidc_req, mock_get):
        """
        Test a scratch module build with provided modulemd and srpms
        """

        file_path = os.path.join(self.cloned_repo_path, "modulemd.yaml")
        pkg1_path = os.path.join(self.cloned_repo_path, "package1.src.rpm")
        pkg2_path = os.path.join(self.cloned_repo_path, "package2.src.rpm")

        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-scratch-build',
            '--srpm',
            pkg1_path,
            '--file',
            file_path,
            '--srpm',
            pkg2_path,
        ]

        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }
        mock_oidc_req.return_value.json.return_value = [{'id': 1094}]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            # we create empty files for the purpose of this test so we don't
            # raise an exception
            open(file_path, 'a').close()
            open(pkg1_path, 'a').close()
            open(pkg2_path, 'a').close()
            cli.module_scratch_build()

        output = sys.stdout.getvalue().strip()
        expected_output = (
            'Submitting the module build...',
            'The build 1094 was submitted to the MBS',
            'Build URLs:',
            cli.cmd.module_get_url(1094, verbose=False),
        )
        self.assertEqual(output, '\n'.join(expected_output))
        mock_get.assert_called_once_with(
            'https://mbs.fedoraproject.org/module-build-service/1/about/',
            timeout=60
        )
        exp_url = ('https://mbs.fedoraproject.org/module-build-service/2/'
                   'module-builds/')
        exp_json = {
            'scmurl': ANY,
            'branch': 'master',
            'scratch': True,
            'modulemd': '',
            'module_name': 'modulemd',
            'srpms': ANY,
            }
        mock_oidc_req.assert_called_once_with(
            exp_url,
            http_method='POST',
            json=exp_json,
            scopes=self.scopes,
            timeout=120)

        args, kwargs = mock_oidc_req.call_args

        # verify that OIDC request srpms argument contains a list of links
        # exactly corresponding to the provided SRPM paths
        srpm_paths = [pkg1_path, pkg2_path]
        req_srpms = kwargs['json']['srpms']
        self.assertEqual(len(req_srpms), len(srpm_paths))
        for srpm_path in srpm_paths:
            filename = os.path.basename(srpm_path)
            srpm_link_regex = '{0}/{1}$'.format(KOJI_UNIQUE_PATH_REGEX.rstrip('$'), filename)
            p = re.compile(srpm_link_regex)
            srpm_link_found = False
            for srpm_link in req_srpms:
                if p.match(srpm_link):
                    srpm_link_found = True
                    break
            self.assertTrue(srpm_link_found,
                            "Did not find srpm {0} amongst {1}".format(filename, req_srpms))

    @patch('sys.stdout', new=StringIO())
    @patch('requests.get')
    @patch('openidc_client.OpenIDCClient.send_request')
    def test_module_cancel(self, mock_oidc_req, mock_get):
        """
        Test canceling a module build when the build exists
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-cancel',
            '1125'
        ]
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }
        mock_rv_two = Mock()
        mock_rv_two.json.return_value = [{'id': 1094}]
        mock_get.side_effect = [mock_rv, mock_rv_two]
        mock_oidc_req.return_value.ok = True

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.module_build_cancel()

        exp_url = ('https://mbs.fedoraproject.org/module-build-service/1/'
                   'about/')
        exp_url_two = ('https://mbs.fedoraproject.org/module-build-service/2/'
                       'module-builds/1125?verbose=true')
        self.assertEqual(mock_get.call_args_list, [
            call(exp_url, timeout=60),
            call(exp_url_two, timeout=60)
        ])
        exp_url_three = ('https://mbs.fedoraproject.org/module-build-service/'
                         '2/module-builds/1125')
        mock_oidc_req.assert_called_once_with(
            exp_url_three,
            http_method='PATCH',
            json={'state': 'failed'},
            scopes=self.scopes,
            timeout=60)
        output = sys.stdout.getvalue().strip()
        expected_output = ('Cancelling module build #1125...\nThe module '
                           'build #1125 was cancelled')
        self.assertEqual(output, expected_output)

    @patch('requests.get')
    @patch('openidc_client.OpenIDCClient.send_request')
    def test_module_cancel_not_found(self, mock_oidc_req, mock_get):
        """
        Test canceling a module build when the build doesn't exist
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-cancel',
            '1125'
        ]
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }
        mock_rv_two = Mock()
        mock_rv_two.ok = False
        mock_rv_two.json.return_value = {
            'status': 404,
            'message': 'No such module found.',
            'error': 'Not Found'
        }
        mock_get.side_effect = [mock_rv, mock_rv_two]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            try:
                cli.module_build_cancel()
                raise RuntimeError('An rpkgError was not raised')
            except rpkgError as error:
                expected_error = ('The following error occurred while getting '
                                  'information on module build #1125:\nNo '
                                  'such module found.')
                self.assertEqual(str(error), expected_error)
        exp_url = ('https://mbs.fedoraproject.org/module-build-service/1/'
                   'about/')
        exp_url_two = ('https://mbs.fedoraproject.org/module-build-service/2/'
                       'module-builds/1125?verbose=true')
        self.assertEqual(mock_get.call_args_list, [
            call(exp_url, timeout=60),
            call(exp_url_two, timeout=60)
        ])
        mock_oidc_req.assert_not_called()

    @patch('sys.stdout', new=StringIO())
    @patch('requests.get')
    @patch('pyrpkg.Commands.kojiweburl', new_callable=PropertyMock)
    def test_module_build_info(self, kojiweburl, mock_get):
        """
        Test getting information on a module build
        """
        kojiweburl.return_value = 'https://koji.example.org/koji'

        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-info',
            '2150'
        ]
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }
        mock_rv_two = Mock()
        mock_rv_two.ok = True
        mock_rv_two.json.return_value = self.module_build_json
        mock_get.side_effect = [mock_rv, mock_rv_two]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.module_build_info()
        exp_url = ('https://mbs.fedoraproject.org/module-build-service/1/'
                   'about/')
        exp_url_two = ('https://mbs.fedoraproject.org/module-build-service/2/'
                       'module-builds/2150?verbose=true')
        self.assertEqual(mock_get.call_args_list, [
            call(exp_url, timeout=60),
            call(exp_url_two, timeout=60)
        ])
        output = sys.stdout.getvalue().strip()
        expected_output = """\
Name:           python3-ecosystem
Stream:         master
Version:        20171010145511
Scratch:        False
Koji Tag:       module-14050f52e62d955b
Owner:          torsava
State:          failed
State Reason:   Some error
Time Submitted: 2017-10-10T14:55:33Z
Time Completed: 2017-10-11T09:42:11Z
Components:
    Name:       module-build-macros
    NVR:        module-build-macros-None-None
    State:      FAILED
    Koji Task:  https://koji.example.org/koji/taskinfo?taskID=22370514

    Name:       python-dns
    NVR:        None
    State:      FAILED
    Koji Task:

    Name:       python-cryptography
    NVR:        None
    State:      FAILED
    Koji Task:
"""  # noqa
        self.maxDiff = None
        self.assertEqual(self.sort_lines(expected_output),
                         self.sort_lines(output))

    @patch('sys.stdout', new=StringIO())
    @patch('requests.get')
    @patch('pyrpkg.ThreadPool', new=FakeThreadPool)
    def test_module_overview(self, mock_get):
        """
        Test the module overview command with 4 modules in the finished state
        and a desired limit of 2
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-overview',
            '--limit',
            '2'
        ]
        # Minimum amount of JSON for the command to succeed
        json_one = {
            'items': [],
            'meta': {
                'next': None
            }
        }
        json_two = {
            'items': [
                {
                    'id': 1100,
                    'koji_tag': 'module-c24f55c24c8fede1',
                    'name': 'testmodule',
                    'owner': 'jkaluza',
                    'state_name': 'ready',
                    'stream': 'master',
                    'version': '20171011093314',
                    'time_modified': '2019-06-03T15:12:06Z',
                },
                {
                    'id': 1099,
                    'koji_tag': 'module-72e94da1453758d8',
                    'name': 'testmodule',
                    'owner': 'jkaluza',
                    'state_name': 'ready',
                    'stream': 'master',
                    "version": "20171011092951",
                    'time_modified': '2019-06-03T14:46:02Z',
                }
            ],
            'meta': {
                'next': ('http://mbs.fedoraproject.org/module-build-service/1/'
                         'module-builds/?state=5&verbose=true&per_page=2&'
                         'order_desc_by=id&page=2')
            }
        }
        json_three = {
            'items': [
                {
                    'id': 1109,
                    'koji_tag': 'module-057fc15e0e44b333',
                    'name': 'testmodule',
                    'owner': 'mprahl',
                    'scratch': True,
                    'state_name': 'failed',
                    'stream': 'master',
                    'version': '20171011173928',
                    'time_modified': '2019-06-03T14:47:12Z',
                },
                {
                    'id': 1094,
                    'koji_tag': 'module-640521aea601c6b2',
                    'name': 'testmodule',
                    'owner': 'mprahl',
                    'state_name': 'failed',
                    'stream': 'master',
                    'version': '20171010151103',
                    'time_modified': '2019-06-03T14:45:26Z',
                }
            ],
            'meta': {
                'next': ('http://mbs.fedoraproject.org/module-build-service/1'
                         '/module-builds/?state=4&verbose=true&per_page=2&'
                         'order_desc_by=id&page=2')
            }
        }

        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {
            'auth_method': 'oidc',
            'api_version': 2
        }
        mock_rv_two = Mock()
        mock_rv_two.ok = True
        mock_rv_two.json.side_effect = [json_one, json_two, json_three]
        mock_get.side_effect = [mock_rv, mock_rv_two, mock_rv_two, mock_rv_two]

        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.module_overview()

        # Can't confirm the call parameters because multithreading makes the
        # order random
        self.assertEqual(mock_get.call_count, 4)
        output = sys.stdout.getvalue().strip()
        expected_output = """
ID:       1100
Name:     testmodule
Stream:   master
Version:  20171011093314
Scratch:  False
Koji Tag: module-c24f55c24c8fede1
Owner:    jkaluza
State:    ready

ID:       1109
Name:     testmodule
Stream:   master
Version:  20171011173928
Scratch:  True
Koji Tag: module-057fc15e0e44b333
Owner:    mprahl
State:    failed
""".strip()
        self.assertEqual(output, expected_output)

    @patch.object(Commands, '_run_command')
    def test_module_build_local(self, mock_run):
        """
        Test submitting a local module build
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-local'
        ]
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            file_path = os.path.join(self.cloned_repo_path, cli.cmd.repo_name + '.yaml')
            # we create an empty file for the purpose of this test so we don't raise an exception
            open(file_path, 'a').close()
            cli.module_build_local()

        mock_run.assert_called_once_with(['mbs-manager', 'build_module_locally', '--file',
                                          file_path, '--stream', 'master'], env={})

    @patch.object(Commands, '_run_command')
    def test_module_build_local_offline_with_repositories(self, mock_run):
        """
        Test submitting a local module build
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-local',
            '--offline',
            '-r', '/etc/yum.repos.d/fedora.repo',
            '-r', '/etc/yum.repos.d/fedora-updates.repo',
        ]
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            file_path = os.path.join(self.cloned_repo_path, cli.cmd.repo_name + '.yaml')
            # we create an empty file for the purpose of this test so we don't raise an exception
            open(file_path, 'a').close()
            cli.module_build_local()

        mock_run.assert_called_once_with(['mbs-manager', 'build_module_locally',
                                          '--offline', '-r', '/etc/yum.repos.d/fedora.repo',
                                          '-r', '/etc/yum.repos.d/fedora-updates.repo', '--file',
                                          file_path, '--stream', 'master'], env={})

    @patch.object(Commands, '_run_command')
    def test_module_build_local_custom_config(self, mock_run):
        """
        Test submitting a local module build
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-local'
        ]
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            cli.config.set("rpkg.mbs", "config_file", "/etc/module-build-service/custom.py")
            cli.config.set("rpkg.mbs", "config_section", "CustomSection")
            file_path = os.path.join(self.cloned_repo_path, cli.cmd.repo_name + '.yaml')
            # we create an empty file for the purpose of this test so we don't raise an exception
            open(file_path, 'a').close()
            cli.module_build_local()

        mock_run.assert_called_once_with(
            ['mbs-manager', 'build_module_locally', '--file', file_path, '--stream', 'master'],
            env={'MBS_CONFIG_FILE': '/etc/module-build-service/custom.py',
                 'MBS_CONFIG_SECTION': 'CustomSection'})

    @patch.object(Commands, '_run_command')
    def test_module_build_local_file_not_found(self, mock_run):
        """
        Test submitting a local module build and raising an IOError exception
        """
        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-local'
        ]
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            with self.assertRaises(IOError):
                cli.module_build_local()

    @patch.object(Commands, '_run_command')
    def test_module_build_local_with_params(self, mock_run):
        """
        Test submitting a local module build with parameters
        """

        file_path = os.path.join(self.cloned_repo_path, 'modulemd.yaml')

        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-local',
            '--file',
            file_path,
            '--stream',
            'test'
        ]
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            # we create an empty file for the purpose of this test so we don't raise an exception
            open(file_path, 'a').close()
            cli.module_build_local()

        mock_run.assert_called_once_with(['mbs-manager', 'build_module_locally', '--file',
                                          file_path, '--stream', 'test'], env={})

    @patch.object(Commands, '_run_command')
    def test_module_build_local_with_modulemd_and_srpms(self, mock_run):
        """
        Test submitting a local module build with provided modulemd and srpms
        """

        file_path = os.path.join(self.cloned_repo_path, 'modulemd.yaml')
        pkg1_path = os.path.join(self.cloned_repo_path, "package1.src.rpm")
        pkg2_path = os.path.join(self.cloned_repo_path, "package2.src.rpm")

        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-local',
            '--file',
            file_path,
            '--srpm',
            pkg1_path,
            '--srpm',
            pkg2_path,
            '--stream',
            'test'
        ]
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            # we create empty files for the purpose of this test so we don't raise an exception
            open(file_path, 'a').close()
            open(pkg1_path, 'a').close()
            open(pkg2_path, 'a').close()
            cli.module_build_local()

        mock_run.assert_called_once_with(['mbs-manager', 'build_module_locally',
                                          '--file', file_path, '--stream', 'test',
                                          '--srpm', pkg1_path, '--srpm', pkg2_path], env={})

    @patch.object(Commands, '_run_command')
    def test_module_build_local_with_skiptests(self, mock_run):
        """
        Test submitting a local module build with skiptests
        """

        file_path = os.path.join(self.cloned_repo_path, "modulemd.yaml")

        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-local',
            '--file',
            file_path,
            '--stream',
            'test',
            '--skip-tests'
        ]
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            # we create an empty file for the purpose of this test so we don't raise an exception
            open(file_path, 'a').close()
            cli.module_build_local()

        mock_run.assert_called_once_with(['mbs-manager', 'build_module_locally', '--skiptests',
                                          '--file', file_path, '--stream', 'test'], env={})

    @patch.object(Commands, '_run_command')
    def test_module_build_local_with_default_streams(self, mock_run):
        """
        Test submitting a local module build with skiptests
        """

        file_path = os.path.join(self.cloned_repo_path, "modulemd.yaml")

        cli_cmd = [
            'rpkg',
            '--path',
            self.cloned_repo_path,
            'module-build-local',
            '--file',
            file_path,
            '--stream',
            'test',
            '-s',
            'foo:bar',
            '--set-default-stream',
            'foo2:bar2',
        ]
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            # we create an empty file for the purpose of this test so we don't raise an exception
            open(file_path, 'a').close()
            cli.module_build_local()

        mock_run.assert_called_once_with(['mbs-manager', 'build_module_locally',
                                          '--file', file_path, '--stream', 'test',
                                          '-s', 'foo:bar', '-s', 'foo2:bar2'], env={})

    @patch.object(Commands, '_run_command')
    def test_module_build_local_with_add_local_builds(self, mock_run):
        """
        Test submitting a local module build with add-local-builds
        """

        file_path = os.path.join(self.cloned_repo_path, "modulemd.yaml")

        cli_cmd = [
            'rpkg',
            '--path', self.cloned_repo_path,
            'module-build-local',
            '--file', file_path,
            '--stream', 'test',
            '--add-local-build', 'testmodule:master:12345678',
            '--add-local-build', 'testmodule2:master:12345678'
        ]
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()
            # we create an empty file for the purpose of this test so we don't raise an exception
            open(file_path, 'a').close()
            cli.module_build_local()

        mock_run.assert_called_once_with([
            'mbs-manager', 'build_module_locally', '--add-local-build',
            'testmodule:master:12345678', '--add-local-build',
            'testmodule2:master:12345678', '--file', file_path, '--stream',
            'test'], env={})

    @patch.object(Commands, '_run_command')
    def test_module_build_local_mbs_manager_is_missing(self, mock_run):
        """
        Test submitting a local module build with mbs-manager missing #1.
        """
        mock_run.side_effect = rpkgError('[Errno 2] No such file or directory')

        cli_cmd = [
            'rpkg', '--path', self.cloned_repo_path, 'module-build-local'
        ]
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()

            # we create an empty file for the purpose of this test so we don't
            # raise an exception
            modulemd_yml = os.path.join(self.cloned_repo_path,
                                        cli.cmd.repo_name + '.yaml')
            self.write_file(modulemd_yml)

            six.assertRaisesRegex(self, rpkgError, r'mbs-manager is missing.+',
                                  cli.module_build_local)

    @patch.object(Commands, '_run_command')
    def test_module_build_local_mbs_manager_is_missing_with_errno(
            self, mock_run):
        """
        Test submitting a local module build with mbs-manager missing #2.
        """
        try:
            exc = FileNotFoundError
        except NameError:
            exc = IOError

        mock_run.side_effect = rpkgError(exc(
            errno.ENOENT,
            "[Errno 2] No such file or directory:"
            " 'mbs-manager': 'mbs-manager'"))

        cli_cmd = [
            'rpkg', '--path', self.cloned_repo_path, 'module-build-local'
        ]
        with patch('sys.argv', new=cli_cmd):
            cli = self.new_cli()

            # we create an empty file for the purpose of this test so we don't
            # raise an exception
            modulemd_yml = os.path.join(self.cloned_repo_path,
                                        cli.cmd.repo_name + '.yaml')
            self.write_file(modulemd_yml)

            six.assertRaisesRegex(self, rpkgError, r'mbs-manager is missing.+',
                                  cli.module_build_local)


class TestOptionNameAndNamespace(CliTestCase):
    """Test CLI option --name and --namespace"""

    create_repo_per_test = False

    @patch('sys.stderr', new_callable=six.StringIO)
    def test_namespace_not_in_configured_distgit_namespaces(self, stderr):
        conf_file = self.get_absolute_conf_filename(
            'rpkg-has-distgit-namespaces.conf')
        cli = [
            'rpkg', '--path', self.cloned_repo_path,
            '--name', 'somepkg', '--namespace', 'somenamespace',
            'srpm'
        ]
        with patch('sys.argv', new=cli):
            with self.assertRaises(SystemExit):
                self.new_cli(conf_file)

    def test_namespace_in_configured_distgit_namespaces(self):
        conf_file = self.get_absolute_conf_filename(
            'rpkg-has-distgit-namespaces.conf')
        cli = [
            'rpkg', '--path', self.cloned_repo_path,
            '--name', 'somepkg', '--namespace', 'modules',
            'srpm'
        ]
        with patch('sys.argv', new=cli):
            cli = self.new_cli(conf_file)
            self.assertEqual('modules', cli.args.repo_namespace)

    def test_only_name(self):
        cli = [
            'rpkg', '--path', self.cloned_repo_path,
            '--name', 'somepkg', 'srpm'
        ]
        with patch('sys.argv', new=cli):
            cli = self.new_cli()
            self.assertEqual('somepkg', cli.cmd.repo_name)
            self.assertEqual('rpms', cli.cmd.ns)

    def test_name_and_namespace_with_distgit_namespace_disabled(self):
        cli = [
            'rpkg', '--path', self.cloned_repo_path,
            '--name', 'somepkg', '--namespace', 'modules', 'srpm'
        ]
        with patch('sys.argv', new=cli):
            cli = self.new_cli()
            self.assertEqual('somepkg', cli.cmd.repo_name)
            self.assertEqual('rpms', cli.cmd.ns)

    def test_name_and_namespace_with_distgit_namespace_enabled(self):
        cli = [
            'rpkg', '--path', self.cloned_repo_path,
            '--name', 'somepkg', '--namespace', 'modules', 'srpm'
        ]
        with patch('sys.argv', new=cli):
            abs_filename = self.get_absolute_conf_filename('rpkg-ns.conf')
            cli = self.new_cli(abs_filename)
            self.assertEqual('somepkg', cli.cmd.repo_name)
            self.assertEqual('modules', cli.cmd.ns)


class TestBuildPackage(FakeKojiCreds, CliTestCase):
    """Test build package, common build, scratch build and chain build"""

    create_repo_per_test = False

    @classmethod
    def setUpClass(cls):
        super(TestBuildPackage, cls).setUpClass()
        cls.checkout_branch(git.Repo(cls.cloned_repo_path), 'rhel-7')

    @classmethod
    def tearDownClass(cls):
        super(TestBuildPackage, cls).tearDownClass()

    def setUp(self):
        super(TestBuildPackage, self).setUp()

        session = self.mock_ClientSession.return_value
        session.getBuildTarget.return_value = {
            'id': 1,
            'name': 'rhel-7-candidate',
            'build_tag': 2,
            'build_tag_name': 'rhel-7-build',
            'dest_tag': 3,
            'dest_tag_name': 'rhel-7-updates-candidate',
        }
        # Get tag, which is the dest_tag_name above.
        session.getTag.return_value = {
            'id': 3,
            'name': 'rhel-7-updates-candidate',
            'locked': False,
        }
        # The full inheritance including parent tags of build tag rhel-7-build
        # above.
        session.getFullInheritance.return_value = [
            {'parent_id': 3},
            {'parent_id': 6},
            {'parent_id': 7},
            {'parent_id': 8},
        ]

        session.build.return_value = 1000
        session.chainBuild.return_value = 2000

        # Write gating.yaml for running tests that test valdation on this file
        # for greenwave.
        self.gating_yaml_content = 'abc'
        with open(os.path.join(self.cloned_repo_path, 'gating.yaml'), 'w') as f:
            f.write(self.gating_yaml_content)

    def tearDown(self):
        super(TestBuildPackage, self).tearDown()

        # Some tests might make changes in the repository for their test
        # purpose. These changes must be cleaned up in order to not impact
        # others to run.
        repo = git.Repo(self.cloned_repo_path)
        if repo.is_dirty():
            self.run_cmd(['git', 'reset', 'HEAD', 'hello.py'],
                         cwd=self.cloned_repo_path)

    def assert_build(self, sub_command, cli_opts=[],
                     expected_chain_urls=None, expected_opts={},
                     config_file=None):
        session = self.mock_ClientSession.return_value

        cli_cmd = [
            'rpkg', '--path', self.cloned_repo_path, '--name', 'docpkg',
            sub_command
        ] + cli_opts

        mock_build_api = None

        with patch('koji_cli.lib.watch_tasks') as watch_tasks:
            with patch('pyrpkg.utils.make_koji_watch_tasks_handler') as mock_ki:
                with patch('sys.argv', new=cli_cmd):
                    cli = self.new_cli(cfg=config_file)
                    if sub_command == 'build':
                        mock_build_api = session.build
                        cli.build()
                    elif sub_command == 'scratch-build':
                        mock_build_api = session.build
                        cli.scratch_build()
                    elif sub_command == 'chain-build':
                        mock_build_api = session.chainBuild
                        cli.chainbuild()

                if '--nowait' in cli_cmd:
                    watch_tasks.assert_not_called()
                else:
                    watch_tasks.assert_called_once_with(
                        session,
                        [mock_build_api.return_value],
                        ki_handler=mock_ki.return_value
                    )
                    self.assertEqual(mock_ki.call_args, (("koji",),))

        mock_build_api.assert_called_once()

        args, kwargs = mock_build_api.call_args
        url, target, opts = args

        self.assertEqual('rhel-7-candidate', target)
        self.assertEqual(expected_opts, opts)

        if sub_command == 'chain-build':
            self.assertEqual(expected_chain_urls, url)
        else:
            if '--srpm' in cli_cmd:
                # Magic guess if a SRPM file name is given.
                i = cli_cmd.index('--srpm')
                if i + 1 >= len(cli_cmd) or cli_cmd[i + 1].startswith('--'):
                    filename = '{0}.src.rpm'.format(cli.cmd.nvr)
                else:
                    filename = os.path.basename(cli_cmd[i + 1])
                match_regex = '{0}/{1}$'.format(
                    KOJI_UNIQUE_PATH_REGEX.rstrip('$'), filename)
                six.assertRegex(self, url, match_regex)
            else:
                expected_url = '{0}#{1}'.format(
                    cli.config.get('rpkg', 'anongiturl', raw=True) % {
                        'repo': 'docpkg'
                    },
                    cli.cmd.commithash,
                )
                self.assertEqual(expected_url, url)

        if '--background' in cli_cmd:
            magic_priority_number = 5
            self.assertEqual(magic_priority_number, kwargs['priority'])

        session.logout.assert_called_once()

        return cli

    def test_normal_build(self):
        self.assert_build('build', expected_opts={})

    def test_scratch_build_command(self):
        self.assert_build('scratch-build', expected_opts={'scratch': True})

    def test_scratch_build_from_build_command_with_scratch_option(self):
        self.assert_build('build',
                          cli_opts=['--scratch'],
                          expected_opts={'scratch': True})

    def test_dont_wait_build_to_finish(self):
        self.assert_build('build',
                          cli_opts=['--scratch', '--nowait'],
                          expected_opts={'scratch': True})

    def assert_option_srpm_use(self, expected_srpm_file=None):
        # Ensure the fake srpm file exists.
        with patch('os.path.exists', return_value=True):
            opts = ['--srpm']
            if expected_srpm_file:
                opts.append(expected_srpm_file)
            cli = self.assert_build('scratch-build',
                                    cli_opts=opts,
                                    expected_opts={'scratch': True})

        session = self.mock_ClientSession.return_value

        session.uploadWrapper.assert_called_once()
        args, kwargs = session.uploadWrapper.call_args

        srpm_file, unique_path = args

        if expected_srpm_file is None:
            self.assertEqual('{0}.src.rpm'.format(cli.cmd.nvr), srpm_file)
        else:
            self.assertEqual(expected_srpm_file, srpm_file)
        six.assertRegex(self, unique_path, r'^cli-build/\d+\.\d+\.[a-zA-Z]+$')
        self.assertEqual({'name': os.path.basename(srpm_file),
                          'callback': koji_cli.lib._progress_callback}, kwargs)

    def test_srpm_option_with_srpm_file(self):
        self.assert_option_srpm_use('/path/to/docpkg-0.1-1.fc28.src.rpm')

    @patch('pyrpkg.Commands.nvr', new_callable=PropertyMock)
    @patch('pyrpkg.Commands._run_command')
    def test_option_srpm_by_generate_srpm_from_repo(self, _run_command, nvr):
        with patch('pyrpkg.layout.build', return_value=MockLayout(root_dir=self.cloned_repo_path)):
            nvr.return_value = 'docpkg-0.1-1.fc28'
            self.assert_option_srpm_use()

        args, kwargs = _run_command.call_args
        self.assertEqual({'shell': True}, kwargs)
        rpmbuild_cmd, = args
        self.assertIn('-bs', rpmbuild_cmd)

    def test_option_background(self):
        self.assert_build('scratch-build',
                          cli_opts=['--background'],
                          expected_opts={'scratch': True})

    def test_option_arches(self):
        self.assert_build(
            'scratch-build',
            cli_opts=['--arches', 'x86_64', 'i686'],
            expected_opts={
                'scratch': True,
                'arch_override': 'x86_64 i686'
            })

    def test_exclusive_arches_with_build_command(self):
        six.assertRaisesRegex(
            self, rpkgError, 'Cannot override arches .+',
            self.assert_build, 'build', cli_opts=['--arches', 'x86_64'])

    def test_option_skip_tag(self):
        self.assert_build('build',
                          cli_opts=['--skip-tag'],
                          expected_opts={'skip_tag': True})

    def test_option_fail_fast(self):
        self.assert_build('build',
                          cli_opts=['--fail-fast'],
                          expected_opts={'fail_fast': True})

    @patch('pyrpkg.Commands.nvr', new_callable=PropertyMock)
    def test_fail_to_get_nvr_but_has_to_check_nvr_existence(self, nvr):
        nvr.side_effect = rpkgError

        six.assertRaisesRegex(
            self, rpkgError, 'Cannot continue .+ constructed NVR',
            self.assert_build, 'build')

    @patch('pyrpkg.Commands.nvr', new_callable=PropertyMock)
    def test_skip_failure_to_get_nvr(self, nvr):
        nvr.side_effect = rpkgError
        self.assert_build('build', cli_opts=['--skip-nvr-check'])

    def test_fail_if_target_does_not_exist(self):
        session = self.mock_ClientSession.return_value
        session.getBuildTarget.return_value = None

        six.assertRaisesRegex(self, rpkgError, 'Unknown build target: .+',
                              self.assert_build, 'build')

    @patch('pyrpkg.Commands.nvr', new_callable=PropertyMock)
    def test_build_fails_if_build_nvr_exists(self, nvr):
        nvr.return_value = 'docpkg-0.1-1.fc28'

        session = self.mock_ClientSession.return_value
        session.getBuild.return_value = {'state': 1}

        six.assertRaisesRegex(
            self, rpkgError,
            'Package docpkg-0.1-1.fc28 has already been built',
            self.assert_build, 'build')

    @patch('pyrpkg.Commands.nvr', new_callable=PropertyMock)
    def test_do_not_check_nvr_existence(self, nvr):
        nvr.return_value = 'docpkg-0.1-1.fc28'

        self.assert_build('build', cli_opts=['--skip-nvr-check'])

        session = self.mock_ClientSession.return_value
        session.getBuild.assert_not_called()

    def test_build_fail_if_repo_has_uncommitted_changed(self):
        self.make_changes(filename='hello.py', content='print()')

        # This regex depends on the error message raised from GitPython.
        six.assertRaisesRegex(
            self, rpkgError, 'has uncommitted changes',
            self.assert_build, 'build')

    @patch('pyrpkg.Commands.nvr', new_callable=PropertyMock)
    @patch('pyrpkg.Commands.commithash', new_callable=PropertyMock)
    @patch('subprocess.Popen')
    def test_chainbuild_do_not_check_nvr_existence(self, Popen, commithash, nvr):
        """checks whether '--skip-nvr-check' parameter is allowed for
        'chain-build'"""
        commithash.return_value = '45678'
        nvr.return_value = 'docpkg-0.1-1.fc28'

        proc = Popen.return_value
        proc.communicate.side_effect = [
            ('12345', ''),
            ('??docpkg (none) 1.2 2.el7??', ''),
        ]
        proc.returncode = 0

        self.assert_build(
            'chain-build',
            cli_opts=['--skip-nvr-check', 'firstpkg'],
            expected_chain_urls=[
                ['git://localhost/firstpkg#12345'],
                ['git://localhost/docpkg#45678'],
            ])

        session = self.mock_ClientSession.return_value
        # check if nvr check was inactive
        session.getBuild.assert_not_called()

    @patch('pyrpkg.Commands.nvr', new_callable=PropertyMock)
    @patch('pyrpkg.Commands.commithash', new_callable=PropertyMock)
    @patch('subprocess.Popen')
    def test_chain_build_without_build_set(self, Popen, commithash, nvr):
        commithash.return_value = '45678'
        nvr.return_value = 'docpkg-0.1-1.fc28'

        Popen.return_value.communicate.side_effect = [
            ('12345', ''),
            ('67890', ''),
        ]

        self.assert_build(
            'chain-build',
            cli_opts=['firstpkg', 'secondpkg'],
            expected_chain_urls=[
                ['git://localhost/firstpkg#12345'],
                ['git://localhost/secondpkg#67890'],
                ['git://localhost/docpkg#45678'],
            ])

    @patch('pyrpkg.Commands.nvr', new_callable=PropertyMock)
    @patch('pyrpkg.Commands.commithash', new_callable=PropertyMock)
    @patch('subprocess.Popen')
    def test_chain_build_in_build_set(self, Popen, commithash, nvr):
        commithash.return_value = '45678'
        nvr.return_value = 'docpkg-0.1-1.fc28'

        Popen.return_value.communicate.side_effect = [
            ('12345', ''),
            ('67890', ''),
            ('2ae3f', ''),
        ]

        self.assert_build(
            'chain-build',
            cli_opts=['firstpkg', 'secondpkg', ':', 'thirdpkg', ':'],
            expected_chain_urls=[
                ['git://localhost/firstpkg#12345',
                 'git://localhost/secondpkg#67890'],
                ['git://localhost/thirdpkg#2ae3f'],
                ['git://localhost/docpkg#45678'],
            ])

    @patch('pyrpkg.Commands.nvr', new_callable=PropertyMock)
    @patch('pyrpkg.Commands.commithash', new_callable=PropertyMock)
    @patch('subprocess.Popen')
    def test_chain_build_by_putting_last_pkg_in_its_own_build_set(
            self, Popen, commithash, nvr):
        commithash.return_value = '45678'
        nvr.return_value = 'docpkg-0.1-1.fc28'

        Popen.return_value.communicate.side_effect = [
            ('12345', ''),
            ('67890', ''),
            ('2ae3f', ''),
        ]

        self.assert_build(
            'chain-build',
            cli_opts=['firstpkg', 'secondpkg', ':', 'thirdpkg'],
            expected_chain_urls=[
                ['git://localhost/firstpkg#12345',
                 'git://localhost/secondpkg#67890'],
                ['git://localhost/thirdpkg#2ae3f',
                 'git://localhost/docpkg#45678'],
            ])

    @patch('requests.post')
    def test_not_allow_to_build_if_gating_yaml_is_invalid(self, post):
        response = Mock(status_code=http_client.BAD_REQUEST)
        response.json.return_value = {'message': 'gating policy is invalid'}
        post.return_value = response

        six.assertRaisesRegex(
            self, rpkgError, 'but it is not valid',
            self.assert_build, 'build',
            config_file=os.path.join(fixtures_dir, 'rpkg-greenwave.conf'))

    @patch('requests.post')
    def test_not_build_if_greenwave_has_internal_error(self, post):
        response = Mock(status_code=http_client.INTERNAL_SERVER_ERROR)
        response.json.return_value = {'message': 'internal error'}
        post.return_value = response

        six.assertRaisesRegex(
            self, rpkgError, 'for an unknown problem',
            self.assert_build, 'build',
            config_file=os.path.join(fixtures_dir, 'rpkg-greenwave.conf'))

    @patch('pyrpkg.cli.cliClient.greenwave_validation_gating')
    def test_skip_gating_policy_validation_if_greenwave_is_not_set(
            self, greenwave_validation_gating):
        self.assert_build('build')
        greenwave_validation_gating.assert_not_called()

    def test_allowed_to_build_if_skipped_gating_yaml_check(self):
        self.assert_build(
            'build',
            cli_opts=['--skip-remote-rules-validation'],
            config_file=os.path.join(fixtures_dir, 'rpkg-greenwave.conf'))

        session = self.mock_ClientSession.return_value
        session.build.assert_called_once()

    @patch('requests.post')
    def test_allowed_to_build_if_gating_yaml_is_correct(self, post):
        response = Mock(status_code=http_client.OK)
        response.json.return_value = {'message': 'gating policy is ok'}
        post.return_value = response

        cli = self.assert_build(
            'build',
            config_file=os.path.join(fixtures_dir, 'rpkg-greenwave.conf'))

        post.assert_called_once_with(
            '{0}/{1}'.format(cli.config.get('rpkg.greenwave', 'url'),
                             'api/v1.0/validate-gating-yaml'),
            data=six.b(self.gating_yaml_content),
            timeout=30)
