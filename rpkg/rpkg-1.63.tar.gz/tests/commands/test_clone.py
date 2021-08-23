import os
import shutil
import tempfile

import git
import pyrpkg

from . import CommandTestCase

CLONE_CONFIG = '''
    bz.default-component %(module)s
    sendemail.to %(module)s-owner@fedoraproject.org
'''


class CommandCloneTestCase(CommandTestCase):
    def test_clone_anonymous(self):
        self.make_new_git(self.module)

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet)
        cmd.clone_config_rpms = CLONE_CONFIG
        cmd.clone(self.module, anon=True)

        moduledir = os.path.join(self.path, self.module)
        self.assertTrue(os.path.isdir(os.path.join(moduledir, '.git')))
        confgit = git.Git(moduledir)
        self.assertIn('gitcred', confgit.config('credential.helper'))
        # there is no namespace used, therefore additional clone config was skipped
        self.assertRaises(git.exc.GitCommandError, confgit.config, 'bz.default-component')
        self.assertRaises(git.exc.GitCommandError, confgit.config, 'sendemail.to')

    def test_clone_anonymous_with_namespace(self):
        self.module = 'rpms/module1'
        self.make_new_git(self.module)

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet, distgit_namespaced=True)
        cmd.clone_config_rpms = CLONE_CONFIG
        cmd.clone(self.module, anon=True)

        moduledir = os.path.join(self.path, 'module1')
        self.assertTrue(os.path.isdir(os.path.join(moduledir, '.git')))
        confgit = git.Git(moduledir)
        self.assertEqual(confgit.config('bz.default-component'), self.module)
        self.assertEqual(confgit.config('sendemail.to'),
                         "%s-owner@fedoraproject.org" % self.module)

    def test_clone_anonymous_with_path(self):
        self.make_new_git(self.module)

        altpath = tempfile.mkdtemp(prefix='rpkg-tests.')

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet)
        cmd.clone(self.module, anon=True, path=altpath)

        moduledir = os.path.join(altpath, self.module)
        self.assertTrue(os.path.isdir(os.path.join(moduledir, '.git')))

        notmoduledir = os.path.join(self.path, self.module)
        self.assertFalse(os.path.isdir(os.path.join(notmoduledir, '.git')))

        shutil.rmtree(altpath)

    def test_clone_anonymous_git_excludes(self):
        self.make_new_git(self.module)

        altpath = tempfile.mkdtemp(prefix='rpkg-tests.')

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet,
                              git_excludes=self.git_excludes)
        cmd.clone(self.module, anon=True)

        moduledir = os.path.join(self.path, self.module)
        self.assertTrue(os.path.isfile(os.path.join(moduledir, '.git/info/exclude')))

        with open(os.path.join(moduledir, '.git/info/exclude')) as git_exclude_file:
            all_excludes = git_exclude_file.read()
            for pattern in self.git_excludes:
                self.assertIn(pattern, all_excludes)

        shutil.rmtree(altpath)

    def test_clone_anonymous_with_branch(self):
        self.make_new_git(self.module,
                          branches=['rpkg-tests-1', 'rpkg-tests-2'])

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet)
        cmd.clone(self.module, anon=True, branch='rpkg-tests-1')

        with open(os.path.join(
                self.path, self.module, '.git', 'HEAD')) as HEAD:
            self.assertEqual(HEAD.read(), 'ref: refs/heads/rpkg-tests-1\n')

    def test_clone_anonymous_with_bare_dir(self):
        self.make_new_git(self.module)

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet)
        cmd.clone(self.module, anon=True, bare_dir='%s.git' % self.module)

        clonedir = os.path.join(self.path, '%s.git' % self.module)
        self.assertTrue(os.path.isdir(clonedir))
        self.assertFalse(os.path.exists(os.path.join(clonedir, 'index')))

    def test_clone_config_template_accepts_base_module(self):
        self.module = 'rpms/module1'
        self.base_module = 'module1'
        self.make_new_git(self.module)

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet, distgit_namespaced=True)
        cmd.clone_config_rpms = 'bz.default-component %(base_module)s'
        cmd.clone(self.module, anon=True)

        moduledir = os.path.join(self.path, 'module1')
        self.assertTrue(os.path.isdir(os.path.join(moduledir, '.git')))
        confgit = git.Git(moduledir)
        self.assertEqual(confgit.config(
                         'bz.default-component'), self.base_module)

    def test_clone_fails_with_both_branch_and_bare_dir(self):
        self.make_new_git(self.module,
                          branches=['rpkg-tests-1', 'rpkg-tests-2'])

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet)

        def raises():
            cmd.clone(self.module, anon=True, branch='rpkg-tests-1',
                      bare_dir='test.git')
        self.assertRaises(pyrpkg.rpkgError, raises)

    def test_clone_into_dir(self):
        self.make_new_git(self.module,
                          branches=['rpkg-tests-1', 'rpkg-tests-2'])

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet)
        cmd.clone(
            self.module, anon=True, branch='rpkg-tests-1', target='new_clone')

        with open(os.path.join(
                self.path, 'new_clone', '.git', 'HEAD')) as HEAD:
            self.assertEqual(HEAD.read(), 'ref: refs/heads/rpkg-tests-1\n')

    def test_clone_into_dir_with_namespace(self):
        self.module = 'rpms/module1'
        self.make_new_git(self.module,
                          branches=['rpkg-tests-1', 'rpkg-tests-2'])

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet, distgit_namespaced=True)
        cmd.clone(
            self.module, anon=True, branch='rpkg-tests-1', target='new_clone')

        with open(os.path.join(
                self.path, 'new_clone', '.git', 'HEAD')) as HEAD:
            self.assertEqual(HEAD.read(), 'ref: refs/heads/rpkg-tests-1\n')

    def test_clone_with_dirs_anonymous(self):
        self.make_new_git(self.module,
                          branches=['rpkg-tests-1', 'rpkg-tests-2'])

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet)
        cmd.clone_config_rpms = CLONE_CONFIG
        cmd.clone_with_dirs(self.module, anon=True)

        moduledir_base = os.path.join(self.path, self.module)
        for branch in ('rpkg-tests-1', 'rpkg-tests-2', 'master'):
            moduledir = os.path.join(moduledir_base, branch)
            self.assertTrue(os.path.isdir(os.path.join(moduledir, '.git')))
            confgit = git.Git(moduledir)
            self.assertIn('gitcred', confgit.config('credential.helper'))
            # there is no namespace used, therefore additional clone config was skipped
            self.assertRaises(git.exc.GitCommandError, confgit.config, 'bz.default-component')
            self.assertRaises(git.exc.GitCommandError, confgit.config, 'sendemail.to')

    def test_clone_with_dirs_anonymous_git_excludes(self):
        self.make_new_git(self.module,
                          branches=['rpkg-tests-1', 'rpkg-tests-2'])

        altpath = tempfile.mkdtemp(prefix='rpkg-tests.')

        cmd = pyrpkg.Commands(self.path, self.lookaside, self.lookasidehash,
                              self.lookaside_cgi, self.gitbaseurl,
                              self.anongiturl, self.branchre, self.kojiprofile,
                              self.build_client, self.user, self.dist,
                              self.target, self.quiet,
                              git_excludes=self.git_excludes)
        cmd.clone_with_dirs(self.module, anon=True)

        moduledir_base = os.path.join(self.path, self.module)
        for branch in ('rpkg-tests-1', 'rpkg-tests-2', 'master'):
            moduledir = os.path.join(moduledir_base, branch)
            self.assertTrue(os.path.isfile(os.path.join(moduledir, '.git/info/exclude')))

            with open(os.path.join(moduledir, '.git/info/exclude')) as git_exclude_file:
                all_excludes = git_exclude_file.read()
                for pattern in self.git_excludes:
                    self.assertIn(pattern, all_excludes)

        shutil.rmtree(altpath)
