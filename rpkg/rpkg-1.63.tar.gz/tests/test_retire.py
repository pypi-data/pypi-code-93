# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import tempfile

import mock
import pyrpkg.cli
import six
from pyrpkg.errors import rpkgError
from six.moves import configparser

# For running tests with Python 2
try:
    import unittest2 as unittest
except ImportError:
    import unittest


TEST_CONFIG = os.path.join(os.path.dirname(__file__), 'fixtures', 'rpkg-ns.conf')


class RetireTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.log = mock.Mock()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _setup_repo(self, origin):
        cmds = (
            ['git', 'init'],
            ['git', 'checkout', '-b', 'master'],
            ['git', 'config', 'user.name', 'John Doe'],
            ['git', 'config', 'user.email', 'jdoe@example.com'],
            ['git', 'remote', 'add', 'origin', origin],
            ['touch', 'rpkg.spec'],
            ['git', 'add', '.'],
            ['git', 'commit', '-m', 'Initial commit'],
        )
        for cmd in cmds:
            subprocess.check_call(
                cmd,
                cwd=self.tmpdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _get_latest_commit(self):
        proc = subprocess.Popen(['git', 'log', '-n', '1', '--pretty=%s'],
                                cwd=self.tmpdir, stdout=subprocess.PIPE,
                                universal_newlines=True)
        out, err = proc.communicate()
        return out.strip()

    def _fake_client(self, args):
        if six.PY2:
            config = configparser.SafeConfigParser()
        else:
            # The SafeConfigParser class has been renamed to ConfigParser in Python 3.2.
            config = configparser.ConfigParser()
        config.read(TEST_CONFIG)
        with mock.patch('sys.argv', new=args):
            client = pyrpkg.cli.cliClient(config, name='rpkg')
            client.do_imports()
            client.setupLogging(self.log)

            client.parse_cmdline()
            client.args.path = self.tmpdir
            client.cmd.push = mock.Mock()
        return client

    def new_client(self, repo, args):
        origin = 'ssh://git@pkgs.example.com/{0}'.format(repo)
        self._setup_repo(origin)
        return self._fake_client(args)

    def assertRetiredPackage(self, reason):
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir,
                                                    'dead.package')))
        self.assertFalse(os.path.isfile(os.path.join(self.tmpdir,
                                                     'rpkg.spec')))
        self.assertEqual(self._get_latest_commit(), reason)

    def assertRetiredModule(self, reason):
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir,
                                                    'dead.module')))
        self.assertFalse(os.path.isfile(os.path.join(self.tmpdir,
                                                     'rpkg.spec')))
        self.assertEqual(self._get_latest_commit(), reason)


class TestPackageRetirement(RetireTestCase):

    def setUp(self):
        super(TestPackageRetirement, self).setUp()

    def tearDown(self):
        super(TestPackageRetirement, self).tearDown()

    def test_package_retire_with_namespace_disallowed(self):
        args = ['rpkg', '--release=master', 'retire', 'my reason']
        client = self.new_client('rpms/rpkg', args)
        # retirement of packages is disabled by default
        self.assertRaises(rpkgError, client.retire)

    def test_package_retire_with_namespace_allowed(self):
        args = ['rpkg', '--release=master', 'retire', 'my reason']
        client = self.new_client('rpms/rpkg', args)
        # un-block retirement of packages
        client.cmd.block_retire_ns.remove('rpms')
        client.retire()

        self.assertRetiredPackage('my reason')
        self.assertEqual(len(client.cmd.push.call_args_list), 1)

    def test_package_retire_without_namespace_disallowed(self):
        args = ['rpkg', '--release=master', 'retire', 'my reason']
        client = self.new_client('rpkg', args)
        # retirement of packages is disabled by default
        self.assertRaises(rpkgError, client.retire)

    def test_package_retire_without_namespace_allowed(self):
        args = ['rpkg', '--release=master', 'retire', 'my reason']
        client = self.new_client('rpkg', args)
        # un-block retirement of packages
        client.cmd.block_retire_ns.remove('rpms')
        client.retire()

        self.assertRetiredPackage('my reason')
        self.assertEqual(len(client.cmd.push.call_args_list), 1)

    def test_package_is_retired_already(self):
        args = ['rpkg', '--release=master', 'retire', 'my reason']
        client = self.new_client('rpkg', args)
        with open(os.path.join(self.tmpdir, 'dead.package'), 'w') as f:
            f.write('dead package')
        client.log = mock.Mock()
        client.retire()
        args, kwargs = client.log.warn.call_args
        self.assertIn('dead.package found, package or module is already retired',
                      args[0])


class TestModuleRetirement(RetireTestCase):

    def setUp(self):
        super(TestModuleRetirement, self).setUp()

    def tearDown(self):
        super(TestModuleRetirement, self).tearDown()

    def test_module_retire_with_namespace_allowed(self):
        args = ['rpkg', '--release=master', 'retire', 'my reason']
        client = self.new_client('modules/rpkg', args)
        # retirement of modules is enabled by default
        client.retire()

        self.assertRetiredModule('my reason')
        self.assertEqual(len(client.cmd.push.call_args_list), 1)

    def test_module_retire_with_namespace_disallowed(self):
        args = ['rpkg', '--release=master', 'retire', 'my reason']
        client = self.new_client('modules/rpkg', args)
        # block retirement of modules
        client.cmd.block_retire_ns.append('modules')
        self.assertRaises(rpkgError, client.retire)

    def test_module_is_retired_already(self):
        args = ['rpkg', '--release=master', 'retire', 'my reason']
        client = self.new_client('rpkg', args)
        with open(os.path.join(self.tmpdir, 'dead.module'), 'w') as f:
            f.write('dead module')
        client.log = mock.Mock()
        client.retire()
        args, kwargs = client.log.warn.call_args
        self.assertIn('dead.module found, package or module is already retired',
                      args[0])
