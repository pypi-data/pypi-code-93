# cli.py - a cli client class module
#
# Copyright (C) 2011 Red Hat Inc.
# Author(s): Jesse Keating <jkeating@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.
#
# There are 6 functions derived from /usr/bin/koji which are licensed under
# LGPLv2.1.  See comments before those functions.

from __future__ import print_function

import argparse
import getpass
import logging
import os
import re
import sys
import textwrap
from gettext import gettext as _  # For `_ArgumentParser'

import koji_cli.lib
import requests
import rpm
import six
from requests.auth import HTTPBasicAuth
from six.moves import configparser

import pyrpkg.utils as utils
from pyrpkg import Modulemd, rpkgError

from .errors import AlreadyUploadedError

# argcomplete might not be available for all products which
# use rpkg as a library (for example centpkg)
try:
    import argcomplete
except ImportError:
    argcomplete = None


# Adds `allow_abbrev' feature
class _ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        sallow_abbrev = 'allow_abbrev'
        self.allow_abbrev = kwargs.get(sallow_abbrev, True)
        if sallow_abbrev in kwargs:
            del kwargs[sallow_abbrev]
        super(_ArgumentParser, self).__init__(*args, **kwargs)

    # We take `argparse.ArgumentParser._parse_optional' from the Python 2.7
    # standard library
    #   https://github.com/python/cpython/blob/2.7/Lib/argparse.py#L2055
    # and combine it with `argparse.ArgumentParser._parse_optional' from the
    # Python 3.6
    #   https://github.com/python/cpython/blob/3.6/Lib/argparse.py#L2083
    def _parse_optional(self, arg_string):
        # if it's an empty string, it was meant to be a positional
        if not arg_string:
            return None

        # if it doesn't start with a prefix, it was meant to be positional
        if not arg_string[0] in self.prefix_chars:
            return None

        # if the option string is present in the parser, return the action
        if arg_string in self._option_string_actions:
            action = self._option_string_actions[arg_string]
            return action, arg_string, None

        # if it's just a single character, it was meant to be positional
        if len(arg_string) == 1:
            return None

        # if the option string before the "=" is present, return the action
        if '=' in arg_string:
            option_string, explicit_arg = arg_string.split('=', 1)
            if option_string in self._option_string_actions:
                action = self._option_string_actions[option_string]
                return action, option_string, explicit_arg

        # This was added from Python 3's argparse library; the rest of
        # _parse_optional remains same as in Python 2's argparse
        # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        if self.allow_abbrev:
            # search through all possible prefixes of the option string
            # and all actions in the parser for possible interpretations
            option_tuples = self._get_option_tuples(arg_string)

            # if multiple actions match, the option string was ambiguous
            if len(option_tuples) > 1:
                options = ', '.join([
                    option_string_
                    for action_, option_string_, explicit_arg_ in option_tuples
                ])
                tup = arg_string, options
                self.error(_('ambiguous option: %s could match %s') % tup)

            # if exactly one action matched, this segmentation is good,
            # so return the parsed action
            elif len(option_tuples) == 1:
                option_tuple, = option_tuples
                return option_tuple
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        # if it was not found as an option, but it looks like a negative
        # number, it was meant to be positional
        # unless there are negative-number-like options
        if self._negative_number_matcher.match(arg_string):
            if not self._has_negative_number_optionals:
                return None

        # if it contains a space, it was meant to be a positional
        if ' ' in arg_string:
            return None

        # it was meant to be an optional but there is no such option
        # in this parser (though it might be a valid option in a subparser)
        return None, arg_string, None


if six.PY2:
    ArgumentParser = _ArgumentParser
else:
    ArgumentParser = argparse.ArgumentParser


class cliClient(object):
    """This is a client class for rpkg clients."""

    def __init__(self, config, name=None):
        """This requires a ConfigParser object

        Name of the app can optionally set, or discovered from exe name
        """

        self.config = config
        self._name = name
        self._oidc_client = None
        # Define default name in child class
        # self.DEFAULT_CLI_NAME = None
        # Property holders, set to none
        self._cmd = None
        self._module = None
        # Set some MBS properties to be None so it can be determined and stored
        # when a module command gets executed
        self._module_api_version = None
        self._module_api_url = None
        # Setup the base argparser
        self.setup_argparser()
        # Add a subparser
        self.subparsers = self.parser.add_subparsers(
            title='Targets',
            description='These are valid commands you can ask %s to do'
                        % self.name)
        # Register all the commands
        self.setup_subparsers()

    @property
    def name(self):
        """Property used to identify prog name and key in config file"""

        if not self._name:
            self._name = self.get_name()
            assert self._name
        return(self._name)

    def get_name(self):
        name = os.path.basename(sys.argv[0])
        if not name or '__main__.py' in name:
            try:
                name = self.DEFAULT_CLI_NAME
            except AttributeError:
                # Ignore missing DEFAULT_CLI_NAME for backwards
                # compatibility
                pass
        if not name:
            # We don't have logger available yet
            raise rpkgError('Could not determine CLI name')
        return name

    # Define some properties here, for lazy loading
    @property
    def cmd(self):
        """This is a property for the command attribute"""

        if not self._cmd:
            self.load_cmd()
        return(self._cmd)

    def _get_bool_opt(self, opt, default=False):
        try:
            return self.config.getboolean(self.name, opt)
        except ValueError:
            raise rpkgError('%s option must be a boolean' % opt)
        except configparser.NoOptionError:
            return default

    def load_cmd(self):
        """This sets up the cmd object"""

        # Set target if we got it as an option
        target = None
        if hasattr(self.args, 'target') and self.args.target:
            target = self.args.target

        # load items from the config file
        items = dict(self.config.items(self.name, raw=True))

        dg_namespaced = self._get_bool_opt('distgit_namespaced')
        la_namespaced = self._get_bool_opt('lookaside_namespaced')

        # Read comma separated list of kerberos realms
        realms = [realm
                  for realm in items.get("kerberos_realms", '').split(',')
                  if realm]

        kojiprofile = None
        if self.config.has_option(self.name, 'kojiprofile'):
            kojiprofile = self.config.get(self.name, 'kojiprofile')

        if not kojiprofile:
            raise rpkgError('Missing kojiprofile to load Koji session.')

        # Read line separated list of git excludes patterns
        git_excludes = [excl
                        for excl in items.get("git_excludes", '').split('\n')
                        if excl]

        results_dir = 'root'
        if self.config.has_option(self.name, 'results_dir'):
            results_dir = self.config.get(self.name, 'results_dir')

        # Create the cmd object
        self._cmd = self.site.Commands(self.args.path,
                                       items['lookaside'],
                                       items['lookasidehash'],
                                       items['lookaside_cgi'],
                                       items['gitbaseurl'],
                                       items['anongiturl'],
                                       items['branchre'],
                                       kojiprofile,
                                       items['build_client'],
                                       user=self.args.user,
                                       dist=self.args.release,
                                       target=target,
                                       quiet=self.args.q,
                                       distgit_namespaced=dg_namespaced,
                                       realms=realms,
                                       lookaside_namespaced=la_namespaced,
                                       git_excludes=git_excludes,
                                       results_dir=results_dir
                                       )

        if self.args.repo_name:
            self._cmd.repo_name = self.args.repo_name
            if dg_namespaced and self.args.repo_namespace:
                self._cmd.ns = self.args.repo_namespace
            else:
                self._cmd.ns = 'rpms'

        self._cmd.password = self.args.password
        self._cmd.runas = self.args.runas
        self._cmd.debug = self.args.debug
        self._cmd.verbose = self.args.v
        self._cmd.lookaside_request_params = items.get('lookaside_request_params')
        self._cmd.dry_run = self.args.dry_run

        # search config for keys "clone_config_{namespace}" and stores its values
        # to object(s): self._cmd.clone_config_{namespace}
        for key in items.keys():
            if re.match(r"^clone_config_\w+$", key):
                clone_config = items.get(key)
                if not clone_config:
                    self.log.debug("No clone config is set for '{0}'".format(key))
                setattr(self._cmd, key, clone_config)

    # This function loads the extra stuff once we figure out what site
    # we are
    def do_imports(self, site=None):
        """Import extra stuff not needed during build

        As a side effect method sets self.site with a loaded library.

        :param site: used to specify which library to load.
        :type site: the module of downstream client that is built on top of
            rpkg.
        """

        # We do some imports here to be more flexible
        if not site:
            import pyrpkg
            self.site = pyrpkg
        else:
            try:
                __import__(site)
                self.site = sys.modules[site]
            except ImportError:
                raise Exception('Unknown site %s' % site)

    def setup_argparser(self):
        """Setup the argument parser and register some basic commands."""

        self.parser = ArgumentParser(
            prog=self.name,
            epilog='For detailed help pass --help to a target',
            allow_abbrev=False)
        # Add some basic arguments that should be used by all.
        # Add a config file
        self.parser.add_argument('--config', '-C',
                                 default=None,
                                 help='Specify a config file to use')
        self.parser.add_argument(
            '--dry-run', action='store_true', default=False,
            help='Perform a dry run.')
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument('--release',
                           dest='release',
                           default=None,
                           help='Override the discovered release from current branch, '
                                'which is used to determine the build target and value of '
                                'dist macro. Generally, release is the name of a branch '
                                'created in your package repository. --release is an alias '
                                'of --dist, hence --release should be used instead.')
        self.parser.add_argument(
            '--name',
            metavar='NAME',
            dest='repo_name',
            help='Override repository name. Use --namespace option to change '
                 'namespace. If not specified, name is discovered from Git '
                 'push URL or Git URL (last part of path with .git extension '
                 'removed) or from Name macro in spec file, in that order.')
        self.parser.add_argument(
            '--namespace',
            metavar='NAMESPACE',
            dest='repo_namespace',
            help='The package repository namespace. If omitted, default to '
                 'rpms if namespace is enabled.')
        # Override the  discovered user name
        self.parser.add_argument('--user', default=None,
                                 help='Override the discovered user name')
        # If using password auth
        self.parser.add_argument('--password', default=None,
                                 help='Password for Koji login')
        # Run Koji commands as a user other then the one you have
        # credentials for (requires configuration on the Koji hub)
        self.parser.add_argument('--runas', default=None,
                                 help='Run Koji commands as a different user')
        # Let the user define a path to work in rather than cwd
        self.parser.add_argument('--path', default=None,
                                 type=utils.u,
                                 help='Define the directory to work in '
                                 '(defaults to cwd)')
        # Verbosity
        self.parser.add_argument('--verbose', '-v', dest='v',
                                 action='store_true',
                                 help='Run with verbose debug output')
        self.parser.add_argument('--debug', '-d', dest='debug',
                                 action='store_true',
                                 help='Run with debug output')
        self.parser.add_argument('-q', action='store_true',
                                 help='Run quietly only displaying errors')

    def setup_subparsers(self):
        """Setup basic subparsers that all clients should use"""

        # Setup some basic shared subparsers

        # help command
        self.register_help()

        # Add a common parsers
        self.register_build_common()
        self.register_container_build_common()
        self.register_module_build_common()
        self.register_rpm_common()

        # Other targets
        self.register_build()
        self.register_chainbuild()
        self.register_clean()
        self.register_clog()
        self.register_clone()
        self.register_copr_build()
        self.register_commit()
        self.register_compile()
        self.register_container_build()
        self.register_container_build_setup()
        self.register_diff()
        if Modulemd is not None:
            self.register_flatpak_build()
        self.register_gimmespec()
        self.register_gitbuildhash()
        self.register_gitcred()
        self.register_giturl()
        self.register_import_srpm()
        self.register_install()
        self.register_lint()
        self.register_list_side_tags()
        self.register_local()
        self.register_mockbuild()
        self.register_mock_config()
        self.register_module_build()
        self.register_module_scratch_build()
        self.register_module_build_cancel()
        self.register_module_build_info()
        self.register_module_local_build()
        self.register_module_build_watch()
        self.register_module_overview()
        self.register_new()
        self.register_new_sources()
        self.register_patch()
        self.register_prep()
        self.register_pull()
        self.register_push()
        self.register_remote()
        self.register_remove_side_tag()
        self.register_request_side_tag()
        self.register_retire()
        self.register_scratch_build()
        self.register_sources()
        self.register_srpm()
        self.register_switch_branch()
        self.register_tag()
        self.register_unused_patches()
        self.register_upload()
        self.register_verify_files()
        self.register_verrel()

    # All the register functions go here.
    def register_help(self):
        """Register the help command."""

        help_parser = self.subparsers.add_parser('help', help='Show usage')
        help_parser.set_defaults(command=self.parser.print_help)

    # Setup a couple common parsers to save code duplication
    def register_build_common(self):
        """Create a common build parser to use in other commands"""

        self.build_parser_common = ArgumentParser(
            'build_common', add_help=False, allow_abbrev=False)
        self.build_parser_common.add_argument(
            '--arches', nargs='*', help='Build for specific arches')
        self.build_parser_common.add_argument(
            '--md5', action='store_const', const='md5', default=None,
            dest='hash', help='Use md5 checksums (for older rpm hosts)')
        self.build_parser_common.add_argument(
            '--nowait', action='store_true', default=False,
            help="Don't wait on build")
        self.build_parser_common.add_argument(
            '--target', default=None,
            help='Define build target to build into')
        self.build_parser_common.add_argument(
            '--background', action='store_true', default=False,
            help='Run the build at a low priority')
        self.build_parser_common.add_argument(
            '--fail-fast', action='store_true', default=False,
            help='Fail the build immediately if any arch fails')
        self.build_parser_common.add_argument(
            '--skip-remote-rules-validation', action='store_true', default=False,
            help=("Don't check if there's a valid gating.yaml file in the repo, where you can "
                  "define additional policies for Greenwave gating."))
        self.build_parser_common.add_argument(
            '--skip-nvr-check', action='store_false', default=True,
            dest='nvr_check',
            help='Submit build to buildsystem without check if NVR was '
                 'already built. NVR is constructed locally and may be '
                 'different from NVR constructed during build on builder.')

    def register_rpm_common(self):
        """Create a common parser for rpm commands"""

        self.rpm_parser_common = ArgumentParser(
            'rpm_common', add_help=False, allow_abbrev=False)
        self.rpm_parser_common.add_argument(
            '--builddir', default=None, help='Define an alternate builddir')
        self.rpm_parser_common.add_argument(
            '--buildrootdir', default=None,
            help='Define an alternate buildrootdir')
        self.rpm_parser_common.add_argument(
            '--arch', help='Prep for a specific arch')
        self.rpm_parser_common.add_argument(
            '--define', help='Pass custom macros to rpmbuild, may specify multiple times',
            action='append')
        self.rpm_parser_common.add_argument(
            "extra_args", default=None, nargs=argparse.REMAINDER,
            help="Custom arguments that are passed to the 'rpmbuild'. "
                 "Use '--' to separate them from other arguments.")

    def register_build(self):
        """Register the build target"""

        build_parser = self.subparsers.add_parser(
            'build', help='Request build', parents=[self.build_parser_common],
            description='This command requests a build of the package in the '
                        'build system. By default it discovers the target '
                        'to build for based on branch data, and uses the '
                        'latest commit as the build source.')
        build_parser.add_argument(
            '--skip-tag', action='store_true', default=False,
            help='Do not attempt to tag package')
        build_parser.add_argument(
            '--scratch', action='store_true', default=False,
            help='Perform a scratch build')
        build_parser.add_argument(
            '--srpm', nargs='?', const='CONSTRUCT',
            help='Build from an srpm. If no srpm is provided with this option'
                 ' an srpm will be generated from current module content.')
        build_parser.set_defaults(command=self.build)

    def register_chainbuild(self):
        """Register the chain build target"""

        chainbuild_parser = self.subparsers.add_parser(
            'chain-build', parents=[self.build_parser_common],
            help='Build current package in order with other packages',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent("""
                Build current package in order with other packages.

                example: %(name)s chain-build libwidget libgizmo

                The current package is added to the end of the CHAIN list.
                Colons (:) can be used in the CHAIN parameter to define groups of
                packages.  Packages in any single group will be built in parallel
                and all packages in a group must build successfully and populate
                the repository before the next group will begin building.

                For example:

                %(name)s chain-build libwidget libaselib : libgizmo :

                will cause libwidget and libaselib to be built in parallel, followed
                by libgizmo and then the current directory package. If no groups are
                defined, packages will be built sequentially.
            """ % {'name': self.name}))
        chainbuild_parser.add_argument(
            'package', nargs='+',
            help='List the packages and order you want to build in')
        chainbuild_parser.set_defaults(command=self.chainbuild)

    def register_clean(self):
        """Register the clean target"""
        clean_parser = self.subparsers.add_parser(
            'clean', help='Remove untracked files',
            description="This command can be used to clean up your working "
                        "directory. By default it will follow .gitignore "
                        "rules. Patterns listed in .git/info/exclude won't"
                        "be removed either.")
        clean_parser.add_argument(
            '--dry-run', '-n', action='store_true', help='Perform a dry-run')
        clean_parser.add_argument(
            '-x', action='store_true',
            help='Do not follow .gitignore and .git/info/exclude rules')
        clean_parser.set_defaults(command=self.clean)

    def register_clog(self):
        """Register the clog target"""

        clog_parser = self.subparsers.add_parser(
            'clog', help='Make a clog file containing top changelog entry',
            description='This will create a file named "clog" that contains '
                        'the latest rpm changelog entry. The leading "- " '
                        'text will be stripped.')
        clog_parser.add_argument(
            '--raw', action='store_true', default=False,
            help='Generate a more "raw" clog without twiddling the contents')
        clog_parser.set_defaults(command=self.clog)

    def register_clone(self):
        """Register the clone target and co alias"""

        clone_parser = self.subparsers.add_parser(
            'clone', help='Clone and checkout a repository',
            description='This command will clone the named repository from '
                        'the configured repository base URL. By default it '
                        'will also checkout the master branch for your '
                        'working copy.')

        # Allow an old style clone with subdirs for branches
        clone_parser.add_argument(
            '--branches', '-B', action='store_true',
            help='Do an old style checkout with subdirs for branches')
        # provide a convenient way to get to a specific branch
        clone_parser.add_argument(
            '--branch', '-b', help='Check out a specific branch')
        # allow to clone without needing a account on the scm server
        clone_parser.add_argument(
            '--anonymous', '-a', action='store_true',
            help='Check out a module anonymously')

        def validator_not_url(raw_value):
            """checks if input doesn't contain URL; URL as an input
            is often mistake"""
            if "://" in raw_value or "@" in raw_value:
                raise argparse.ArgumentTypeError("argument can't contain an URL")
            return raw_value
        # store the module to be cloned
        clone_parser.add_argument(
            'repo', nargs=1, type=validator_not_url,
            help="Name of the repository to clone. "
                 "It should not be a Git URL. "
                 "Should be 'namespace/repo-name' in case of namespaced dist-git. "
                 "Otherwise, just 'repo-name'. "
                 "Namespace examples are 'rpms', 'container', 'modules', 'flatpaks'. "
                 "Default namespace 'rpms' can be ignored. ")
        # Eventually specify where to clone the module
        clone_parser.add_argument(
            "clone_target", default=None, nargs="?",
            help='Directory in which to clone the repository')
        clone_parser.add_argument(
            "extra_args", default=None, nargs=argparse.REMAINDER,
            help="Custom arguments that are passed to the 'git clone'. "
                 "Use '--' to separate them from other arguments.")

        def validator_integer_string(raw_value):
            """checks if input is string that contains integer number"""
            try:
                value = str(int(raw_value))
            except (ValueError, TypeError):
                raise argparse.ArgumentTypeError("argument has to be a number")
            return value
        clone_parser.add_argument(
            '--depth', type=validator_integer_string,
            help='Create a shallow clone with a history truncated '
                 'to the specified number of commits')
        clone_parser.set_defaults(command=self.clone)

        # Add an alias for historical reasons
        co_parser = self.subparsers.add_parser(
            'co', parents=[clone_parser], conflict_handler='resolve',
            help='Alias for clone')
        co_parser.set_defaults(command=self.clone)

    def register_commit(self):
        """Register the commit target and ci alias"""

        commit_parser = self.subparsers.add_parser(
            'commit', help='Commit changes',
            description='This invokes a git commit. All tracked files with '
                        'changes will be committed unless a specific file '
                        'list is provided. $EDITOR will be used to generate a'
                        ' changelog message unless one is given to the '
                        'command. A push can be done at the same time.')
        commit_parser.add_argument(
            '-m', '--message', default=None,
            help='Use the given <msg> as the commit message summary')
        commit_parser.add_argument(
            '--with-changelog',
            action='store_true',
            default=None,
            help='Get the last changelog from SPEC as commit message content. '
                 'This option must be used with -m together.')
        commit_parser.add_argument(
            '-c', '--clog', default=False, action='store_true',
            help='Generate the commit message from the Changelog section')
        commit_parser.add_argument(
            '--raw', action='store_true', default=False,
            help='Make the clog raw')
        commit_parser.add_argument(
            '-t', '--tag', default=False, action='store_true',
            help='Create a tag for this commit')
        commit_parser.add_argument(
            '-F', '--file', default=None,
            help='Take the commit message from the given file')
        # allow one to commit /and/ push at the same time.
        commit_parser.add_argument(
            '-p', '--push', default=False, action='store_true',
            help='Commit and push as one action')
        # Allow a list of files to be committed instead of everything
        commit_parser.add_argument(
            'files', nargs='*', default=[],
            help='Optional list of specific files to commit')
        commit_parser.add_argument(
            '-s', '--signoff', default=False, action='store_true',
            help='Include a signed-off-by')
        commit_parser.set_defaults(command=self.commit)

        # Add a ci alias
        ci_parser = self.subparsers.add_parser(
            'ci', parents=[commit_parser], conflict_handler='resolve',
            help='Alias for commit')
        ci_parser.set_defaults(command=self.commit)

    def register_compile(self):
        """Register the compile target"""

        compile_parser = self.subparsers.add_parser(
            'compile', parents=[self.rpm_parser_common],
            help='Local test rpmbuild compile',
            description='This command calls rpmbuild to compile the source. '
                        'By default the prep and configure stages will be '
                        'done as well, unless the short-circuit option is '
                        'used.')
        compile_parser.add_argument('--short-circuit',
                                    action='store_true',
                                    help='short-circuit compile')
        compile_parser.add_argument('--nocheck',
                                    action='store_true',
                                    help='nocheck compile')
        compile_parser.set_defaults(command=self.compile)

    def register_diff(self):
        """Register the diff target"""

        diff_parser = self.subparsers.add_parser(
            'diff', help='Show changes between commits, commit and working '
                         'tree, etc',
            description='Use git diff to show changes that have been made to '
                        'tracked files. By default cached changes (changes '
                        'that have been git added) will not be shown.')
        diff_parser.add_argument(
            '--cached', default=False, action='store_true',
            help='View staged changes')
        diff_parser.add_argument(
            'files', nargs='*', default=[],
            help='Optionally diff specific files')
        diff_parser.set_defaults(command=self.diff)

    def register_gimmespec(self):
        """Register the gimmespec target"""

        gimmespec_parser = self.subparsers.add_parser(
            'gimmespec', help='Print the spec file name')
        gimmespec_parser.set_defaults(command=self.gimmespec)

    def register_gitbuildhash(self):
        """Register the gitbuildhash target"""

        gitbuildhash_parser = self.subparsers.add_parser(
            'gitbuildhash',
            help='Print the git hash used to build the provided n-v-r',
            description='This will show you the commit hash string used to '
                        'build the provided build n-v-r')
        gitbuildhash_parser.add_argument(
            'build', help='name-version-release of the build to query.')
        gitbuildhash_parser.set_defaults(command=self.gitbuildhash)

    def register_gitcred(self):
        """Register the (hidden) gitcred target

        These commands implement the git-credential helper API, so that we are
        able to provide OpenID Connect/OAuth2 tokens if requested for https
        based pushing.
        """

        gitcred_parser = self.subparsers.add_parser(
            'gitcred',
            add_help=False)
        cred_subs = gitcred_parser.add_subparsers()
        get_parser = cred_subs.add_parser('get')
        get_parser.set_defaults(command=self.gitcred_get)
        store_parser = cred_subs.add_parser('store')
        store_parser.set_defaults(command=self.gitcred_store)
        erase_parser = cred_subs.add_parser('erase')
        erase_parser.set_defaults(command=self.gitcred_erase)

    def gitcred_store(self):
        """Nothing to do here.

        .. versionadded:: 1.55

        If we returned a token, that's already stored. If the user manually
        entered a password, we do not want to store it. Thus we present to you,
        a no-op.
        """
        pass

    def _gitcred_check_input(self):
        """Parses the git-credential-helper IO format input."""
        inp = {}
        for line in sys.stdin:
            vals = line.split('=', 2)
            if len(vals) != 2:
                print('Invalid input: %s' % line, file=sys.stderr)
                return False
            key, val = vals
            inp[key] = val.strip()

        if inp['protocol'] != 'https':
            # Nothing to do for us here
            return False
        return inp

    def _gitcred_return(self, args):
        """Returns git-credential-helper IO format output."""
        for arg in args:
            print('%s=%s' % (arg, args[arg]))
        print('')

    @property
    def oidc_configured(self):
        """Returns a boolean indicating whether OIDC is configured.

        .. versionadded:: 1.55

        :return: True if OIDC is configured. False otherwise.
        :rtype: bool
        """
        for opt in ['oidc_id_provider', 'oidc_client_id', 'oidc_client_secret',
                    'oidc_scopes']:
            if not self.config.has_option(self.name, opt):
                return False

        return True

    @property
    def oidc_client(self):
        """Returns a OpenID Connect client reference.

        .. versionadded:: 1.55

        :return: client if configured, None if unconfigured.
        :rtype: openidc_client.OpenIDCClient or None
        """
        if self._oidc_client:
            return self._oidc_client

        if not self.oidc_configured:
            print('OpenID Connect not configured', file=sys.stderr)
            return None

        import openidc_client
        self._oidc_client = openidc_client.OpenIDCClient(
            self.name,
            self.config.get(self.name, 'oidc_id_provider'),
            {'Token': 'Token', 'Authorization': 'Authorization'},
            self.config.get(self.name, 'oidc_client_id'),
            self.config.get(self.name, 'oidc_client_secret'),
            printfd=sys.stderr)
        return self._oidc_client

    @property
    def _oidc_scopes(self):
        """Returns the configured OIDC scopes to request."""
        return self.config.get(self.name, 'oidc_scopes').split(',')

    def _oidc_token(self, **kwargs):
        """Returns an OpenID Connect token via the global client.

        Returns: (string or bool or None): Returns a string token, None if the
            client did not return a token, or False if the client was not configured.
        """
        client = self.oidc_client
        if not client:
            return False
        return client.get_token(self._oidc_scopes, **kwargs)

    def _gitcred_test(self, args):
        """Test the token we are about to return for freshness.

        Note that this is a best-effort, and it could be that we return scucess
        but the actual push fails, in which case git will call the erase method,
        and we tell the user to retry.
        """
        # 'path' is provided if git config credential.useHttpPath is true
        if 'path' in args:
            # Without "path", we can't really test...
            url = '%(protocol)s://%(host)s/%(path)s/info/refs?service=git-receive-pack' % args
            resp = requests.head(url, auth=HTTPBasicAuth(args['username'],
                                                         args['password']))
            if resp.status_code == 401:
                return self.oidc_client.report_token_issue()

    def gitcred_get(self):
        """Performs the git-credential-helper get operation.

        .. versionadded:: 1.55
        """
        args = self._gitcred_check_input()
        if not args:
            return
        token = self._oidc_token()
        if token is False:
            # This happens if OpenID Connect was unconfigured. Don't tell git
            # to quit, so that users get a fighting chance to enter a password
            # by hand.
            self._gitcred_return(args)
            return
        # If, however, we are configured to use OpenID Connect, and we just
        # didn't get a (valid) token, tell git to not ask the user, since they
        # won't be able to manually provide a valid token.
        args['quit'] = '1'
        if not token:
            self._gitcred_return(args)
            print('No token received.', file=sys.stderr)
            return
        args['username'] = '-openidc-'
        args['password'] = token
        newtoken = self._gitcred_test(args)
        if newtoken is not None:
            args['password'] = newtoken
        self._gitcred_return(args)

    def gitcred_erase(self):
        """Performs the git-credential-helper erase operation.

        .. versionadded:: 1.55
        """
        args = self._gitcred_check_input()
        if not args:
            return
        token = self._oidc_token(new_token=False)
        if token and token == args.get('password'):
            newtoken = self.oidc_client.report_token_issue()
            if newtoken is None:
                print('Issue with your token renewal', file=sys.stderr)
            else:
                print('Token was renewed. Please rerun command',
                      file=sys.stderr)

    def register_giturl(self):
        """Register the giturl target"""

        giturl_parser = self.subparsers.add_parser(
            'giturl', help='Print the git url for building',
            description='This will show you which git URL would be used in a '
                        'build command. It uses the git hashsum of the HEAD '
                        'of the current branch (which may not be pushed).')
        giturl_parser.set_defaults(command=self.giturl)

    def register_import_srpm(self):
        """Register the import-srpm target"""

        import_srpm_parser = self.subparsers.add_parser(
            'import', help='Import srpm content into a module',
            description='This will extract sources, patches, and the spec '
                        'file from an srpm and update the current module '
                        'accordingly. It will import to the current branch by '
                        'default.')
        import_srpm_parser.add_argument(
            '--skip-diffs', help="Don't show diffs when import srpms",
            action='store_true')
        import_srpm_parser.add_argument(
            '--offline', help='Do not upload files into lookaside cache',
            action='store_true')
        import_srpm_parser.add_argument('srpm', help='Source rpm to import')
        import_srpm_parser.set_defaults(command=self.import_srpm)

    def register_install(self):
        """Register the install target"""

        install_parser = self.subparsers.add_parser(
            'install', parents=[self.rpm_parser_common],
            help='Local test rpmbuild install',
            description='This will call rpmbuild to run the install section. '
                        'All leading sections will be processed as well, '
                        'unless the short-circuit option is used.')
        install_parser.add_argument(
            '--short-circuit',
            action='store_true',
            default=False,
            help='short-circuit install')
        install_parser.add_argument(
            '--nocheck',
            action='store_true',
            help='nocheck install')
        install_parser.set_defaults(command=self.install, default=False)

    def register_lint(self):
        """Register the lint target"""

        lint_parser = self.subparsers.add_parser(
            'lint', help='Run rpmlint against local spec and build output if '
                         'present.',
            description='Rpmlint can be configured using the --rpmlintconf/-r'
                         ' option or by setting a <pkgname>.rpmlintrc file in '
                         'the working directory')
        lint_parser.add_argument(
            '--info', '-i', default=False, action='store_true',
            help='Display explanations for reported messages')
        lint_parser.add_argument(
            '--rpmlintconf', '-r', default=None,
            help='Use a specific configuration file for rpmlint')
        lint_parser.set_defaults(command=self.lint)

    def register_list_side_tags(self):
        """Register the list-side-tags target"""

        parser = self.subparsers.add_parser(
            "list-side-tags", help="List existing side-tags",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--mine", action="store_true", help="List only my side tags")
        group.add_argument(
            "--user", dest="tag_owner", help="List side tags created by this user",
        )
        group.add_argument("--base-tag", help="List only tags based on this base")
        parser.set_defaults(command=self.list_side_tags)

    def register_local(self):
        """Register the local target"""

        local_parser = self.subparsers.add_parser(
            'local', parents=[self.rpm_parser_common],
            help='Local test rpmbuild binary',
            description='Locally test run of rpmbuild producing binary RPMs. '
                        'The rpmbuild output will be logged into a file named'
                        ' .build-%{version}-%{release}.log')
        # Allow the user to just pass "--md5" which will set md5 as the
        # hash, otherwise use the default of sha256
        local_parser.add_argument(
            '--md5', action='store_const', const='md5', default=None,
            dest='hash', help='Use md5 checksums (for older rpm hosts)')
        # Pass --with/without options to rpmbuild
        local_parser.add_argument(
            '--with', help='Enable configure option (bcond) for the build',
            dest='bcond_with', action='append')
        local_parser.add_argument(
            '--without', help='Disable configure option (bcond) for the build',
            dest='bcond_without', action='append')
        local_parser.set_defaults(command=self.local)

    def register_new(self):
        """Register the new target"""

        new_parser = self.subparsers.add_parser(
            'new', help='Diff against last tag',
            description='This will use git to show a diff of all the changes '
                        '(even uncommitted changes) since the last git tag '
                        'was applied.')
        new_parser.set_defaults(command=self.new)

    def register_mockbuild(self):
        """Register the mockbuild target"""

        mockbuild_parser = self.subparsers.add_parser(
            'mockbuild', help='Local test build using mock',
            description='This will use the mock utility to build the package '
                        'for the distribution detected from branch '
                        'information. This can be overridden using the global'
                        ' --release option. Your user must be in the local '
                        '"mock" group.',
                        epilog="If config file for mock isn't found in the "
                               "/etc/mock directory, a temporary config "
                               "directory for mock is created and populated "
                               "with a config file created with mock-config.")
        mockbuild_parser.add_argument(
            '--root', '--mock-config', metavar='CONFIG',
            dest='root', help='Override mock configuration (like mock -r)')
        # Allow the user to just pass "--md5" which will set md5 as the
        # hash, otherwise use the default of sha256
        mockbuild_parser.add_argument(
            '--md5', action='store_const', const='md5', default=None,
            dest='hash', help='Use md5 checksums (for older rpm hosts)')
        mockbuild_parser.add_argument(
            '--no-clean', '-n', help='Do not clean chroot before building '
            'package', action='store_true')
        mockbuild_parser.add_argument(
            '--no-cleanup-after', help='Do not clean chroot after building '
            '(if automatic cleanup is enabled', action='store_true')
        mockbuild_parser.add_argument(
            '--no-clean-all', '-N', help='Alias for both --no-clean and '
            '--no-cleanup-after', action='store_true')
        mockbuild_parser.add_argument(
            '--with', help='Enable configure option (bcond) for the build',
            dest='bcond_with', action='append')
        mockbuild_parser.add_argument(
            '--without', help='Disable configure option (bcond) for the build',
            dest='bcond_without', action='append')
        mockbuild_parser.add_argument(
            '--shell', action='store_true',
            help='Run commands interactively within chroot. Before going into'
                 ' chroot, mockbuild needs to run with --no-cleanup-after '
                 'in advanced.')
        mockbuild_parser.add_argument(
            '--enablerepo', action='append',
            help='Pass enablerepo option to yum/dnf (may be used more than once)')
        mockbuild_parser.add_argument(
            '--disablerepo', action='append',
            help='Pass disablerepo option to yum/dnf (may be used more than once)')
        mockbuild_parser.add_argument(
            '--enable-network', action='store_true', help='Enable networking')
        mockbuild_parser.add_argument(
            "extra_args", default=None, nargs=argparse.REMAINDER,
            help="Custom arguments that are passed to the 'mock'. "
                 "Use '--' to separate them from other arguments.")
        mockbuild_parser.set_defaults(command=self.mockbuild)

    def register_mock_config(self):
        """Register the mock-config target"""

        mock_config_parser = self.subparsers.add_parser(
            'mock-config', help='Generate a mock config',
            description='This will generate a mock config based on the '
                        'buildsystem target')
        mock_config_parser.add_argument(
            '--target', help='Override target used for config', default=None)
        mock_config_parser.add_argument('--arch', help='Override local arch')
        mock_config_parser.set_defaults(command=self.mock_config)

    def register_module_build_common(self):
        """Create a common module build parser to use in other commands"""

        parser = ArgumentParser(
            'module_build_common', add_help=False, allow_abbrev=False)
        self.module_build_parser_common = parser
        parser.add_argument(
            'scm_url', nargs='?',
            help='The module\'s SCM URL. This defaults to the current repo.')
        parser.add_argument(
            'branch', nargs='?',
            help=('The module\'s SCM branch. This defaults to the current '
                  'checked-out branch.'))
        parser.add_argument(
            '--watch', '-w', help='Watch the module build',
            action='store_true')
        parser.add_argument(
            '--buildrequires', action='append', metavar='name:stream',
            dest='buildrequires', type=utils.validate_module_dep_override,
            help='Buildrequires to override in the form of "name:stream"')
        parser.add_argument(
            '--requires', action='append', metavar='name:stream',
            dest='requires', type=utils.validate_module_dep_override,
            help='Requires to override in the form of "name:stream"')
        optional_help_msg = (
            'MBS optional arguments in the form of "key=value". For example: '
            "'{0} module-build --optional \"reuse_components_from=<NSVC>\"'. "
            "More description including list of available arguments here: "
            "https://pagure.io/fm-orchestrator/")
        parser.add_argument(
            '--optional', action='append', metavar='key=value',
            dest='optional', type=utils.validate_module_build_optional,
            help=optional_help_msg.format(self.name))
        parser.add_argument(
            '--file', nargs='?', dest='file_path',
            help='The modulemd yaml file for module scratch build.')
        parser.add_argument(
            '--srpm', action='append', dest='srpms',
            help='Include one or more srpms for module scratch build.')

    def register_module_build(self):
        sub_help = 'Build a module using MBS'
        self.module_build_parser = self.subparsers.add_parser(
            'module-build', parents=[self.module_build_parser_common],
            help=sub_help, description=sub_help)
        self.module_build_parser.add_argument(
            '--scratch', action='store_true', default=False,
            help='Perform a scratch build')
        self.module_build_parser.set_defaults(command=self.module_build)

    def register_module_scratch_build(self):
        sub_help = 'Build a scratch module using MBS'
        self.module_build_parser = self.subparsers.add_parser(
            'module-scratch-build', parents=[self.module_build_parser_common],
            help=sub_help, description=sub_help)
        self.module_build_parser.set_defaults(command=self.module_scratch_build)

    def register_module_build_cancel(self):
        sub_help = 'Cancel an MBS module build'
        self.module_build_cancel_parser = self.subparsers.add_parser(
            'module-build-cancel', help=sub_help, description=sub_help)
        self.module_build_cancel_parser.add_argument(
            'build_id', help='The ID of the module build to cancel', type=int)
        self.module_build_cancel_parser.set_defaults(
            command=self.module_build_cancel)

    def register_module_build_info(self):
        sub_help = 'Show information of an MBS module build'
        self.module_build_info_parser = self.subparsers.add_parser(
            'module-build-info', help=sub_help, description=sub_help)
        self.module_build_info_parser.add_argument(
            'build_id', help='The ID of the module build', type=int)
        self.module_build_info_parser.set_defaults(
            command=self.module_build_info)

    def register_module_local_build(self):
        sub_help = 'Build a module locally using the mbs-manager command'
        self.module_build_local_parser = self.subparsers.add_parser(
            'module-build-local', help=sub_help, description=sub_help)
        self.module_build_local_parser.add_argument(
            '--file', nargs='?', dest='file_path',
            help=('The module\'s modulemd yaml file. If not specified, a yaml file'
                  ' with the same basename as the name of the repository will be used.'))
        self.module_build_local_parser.add_argument(
            '--srpm', action='append', dest='srpms',
            help='Include one or more srpms for module build.')
        self.module_build_local_parser.add_argument(
            '--stream', nargs='?', dest='stream',
            help=('The module\'s stream/SCM branch. This defaults to the current '
                  'checked-out branch.'))
        self.module_build_local_parser.add_argument(
            '--skip-tests', help='Adds a macro for skipping the check section',
            action='store_true', dest='skiptests')
        self.module_build_local_parser.add_argument(
            '--add-local-build', action='append', dest='local_builds_nsvs',
            metavar='N:S:V',
            help=('Import previously finished local module builds into MBS in '
                  'the format of name:stream or name:stream:version'))
        self.module_build_local_parser.add_argument(
            '-s', '--set-default-stream', action='append', default=[],
            dest='default_streams', metavar='N:S',
            help=('Set the default stream for given module dependency in case '
                  'there are multiple streams to choose from.'))
        self.module_build_local_parser.add_argument(
            '--offline',
            help='Builds module offline without any external infrastructure',
            action='store_true', dest='offline')
        self.module_build_local_parser.add_argument(
            '-r', '--repository', action='append', dest='base_module_repositories',
            metavar='PATH',
            help=('Full path to .repo file defining the base module repository '
                  'to use when --offline is used.'))
        self.module_build_local_parser.set_defaults(
            command=self.module_build_local)

    def register_module_build_watch(self):
        sub_help = 'Watch an MBS build'
        self.module_build_watch_parser = self.subparsers.add_parser(
            'module-build-watch', help=sub_help, description=sub_help)
        self.module_build_watch_parser.add_argument(
            'build_id', type=int, nargs='+',
            help='The ID of the module build to watch')
        self.module_build_watch_parser.set_defaults(
            command=self.module_build_watch)

    def register_module_overview(self):
        sub_help = 'Shows an overview of MBS builds'
        self.module_overview_parser = self.subparsers.add_parser(
            'module-overview', help=sub_help, description=sub_help)
        self.module_overview_parser.add_argument(
            '--unfinished', help='Show unfinished module builds',
            default=False, action='store_true')
        self.module_overview_parser.add_argument(
            '--limit', default=10, type=int,
            help='The number of most recent module builds to display')
        group = self.module_overview_parser.add_mutually_exclusive_group()
        group.add_argument(
            '--owner', metavar='FAS_ID', help='List only items of that owner')
        group.add_argument(
            '--mine', action='store_true', default=False,
            help='Use current Kerberos name or username')
        self.module_overview_parser.set_defaults(
            command=self.module_overview)

    def register_new_sources(self):
        """Register the new-sources target"""

        # Make it part of self to be used later
        self.new_sources_parser = self.subparsers.add_parser(
            'new-sources',
            help='Upload source files',
            description='This will upload new source file(s) to lookaside '
                        'cache, and all file names listed in sources file '
                        'will be replaced. .gitignore will be also updated '
                        'with new uploaded file(s). Please remember to '
                        'commit them.')
        self.new_sources_parser.add_argument(
            '--offline',
            help='Do all the steps except uploading into lookaside cache',
            action='store_true', dest='offline')
        self.new_sources_parser.add_argument('files', nargs='+')
        self.new_sources_parser.set_defaults(command=self.new_sources, replace=True)

    def register_patch(self):
        """Register the patch target"""

        patch_parser = self.subparsers.add_parser(
            'patch', help='Create and add a gendiff patch file',
            epilog='Patch file will be named: package-version-suffix.patch '
                   'and the file will be added to the repo index')
        patch_parser.add_argument(
            '--rediff', action='store_true', default=False,
            help='Recreate gendiff file retaining comments Saves old patch '
                 'file with a suffix of ~')
        patch_parser.add_argument(
            'suffix', help='Look for files with this suffix to diff')
        patch_parser.set_defaults(command=self.patch)

    def register_prep(self):
        """Register the prep target"""

        prep_parser = self.subparsers.add_parser(
            'prep', parents=[self.rpm_parser_common],
            help='Local test rpmbuild prep',
            description='Use rpmbuild to "prep" the sources (unpack the '
                        'source archive(s) and apply any patches.)')
        prep_parser.set_defaults(command=self.prep)

    def register_pull(self):
        """Register the pull target"""

        pull_parser = self.subparsers.add_parser(
            'pull', help='Pull changes from the remote repository and update '
                         'the working copy.',
            description='This command uses git to fetch remote changes and '
                        'apply them to the current working copy. A rebase '
                        'option is available which can be used to avoid '
                        'merges.',
            epilog='See git pull --help for more details')
        pull_parser.add_argument(
            '--rebase', action='store_true',
            help='Rebase the locally committed changes on top of the remote '
                 'changes after fetching. This can avoid a merge commit, but '
                 'does rewrite local history.')
        pull_parser.add_argument(
            '--no-rebase', action='store_true',
            help='Do not rebase, overriding .git settings to the contrary')
        pull_parser.set_defaults(command=self.pull)

    def register_push(self):
        """Register the push target"""

        push_parser = self.subparsers.add_parser(
            'push', help='Push changes to remote repository')
        push_parser.add_argument('--force', '-f', help='Force push', action='store_true')
        push_parser.set_defaults(command=self.push)

    def register_remote(self):
        """
            Add command remote and options
            Experimental function
        """
        remote_parser = self.subparsers.add_parser(
            'remote',
            help='Operations with tracked repositories (\'remotes\'). '
                 'This is an experimental interface.')

        remote_subparsers = remote_parser.add_subparsers(
            dest='remote_action',
            description='Operations with tracked repositories (\'remotes\'). '
                        'This is an experimental interface. '
                        'Please note that some or all current functionality is subject to change. '
                        'Without parameters list of remotes will be shown.')

        remote_add_parser = remote_subparsers.add_parser(
            'add',
            description='Adds a new dist-git repository as a remote to the current repository. '
                        'Uses repositories URLs from {}\'s config.'.format(self.name))

        default_remote_name = self.name

        if self.config.has_option(self.name, 'default_remote_name'):
            default_remote_name = self.config.get(self.name, 'default_remote_name')

            # the default remote name is either set as something specific or it's
            # an empty string, and if it's an empty string we set it to the default.
            if default_remote_name == '':
                default_remote_name = self.name

        remote_add_parser.add_argument(
            '--remote-name',
            help='User can set own name for remote; Default value={}.'.format(default_remote_name),
            default=default_remote_name)
        remote_add_parser.add_argument(
            '--repo-name',
            help='Specify repo to add from source; Default to repo in working directory.')

        remote_parser.set_defaults(command=self.remote)

    def register_remove_side_tag(self):
        """Register remove-side-tag command."""
        parser = self.subparsers.add_parser(
            "remove-side-tag", help="Remove a side tag (without merging packages)"
        )
        parser.add_argument("TAG", help="name of tag to be deleted")
        parser.set_defaults(command=self.remove_side_tag)

    def register_request_side_tag(self):
        """Register command line parser for subcommand request-side-tag """
        parser = self.subparsers.add_parser(
            "request-side-tag", help="Create a new side tag"
        )
        parser.add_argument("--base-tag", help="name of base tag")
        parser.add_argument(
            "--suffix",
            help=(
                "A suffix to be appended to the side tag name. "
                "The suffix must be allowed in Koji configuration."
            )
        )
        parser.set_defaults(command=self.request_side_tag)

    def register_retire(self):
        """Register the retire target"""

        retire_parser = self.subparsers.add_parser(
            'retire', help='Retire a package/module',
            description='This command will remove all files from the repo, '
                        'leave a dead.package file for rpms or dead.module '
                        'file for modules, and push the changes.'
        )
        retire_parser.add_argument('reason',
                                   help='Reason for retiring the package/module')
        retire_parser.set_defaults(command=self.retire)

    def register_scratch_build(self):
        """Register the scratch-build target"""

        scratch_build_parser = self.subparsers.add_parser(
            'scratch-build', help='Request scratch build',
            parents=[self.build_parser_common],
            description='This command will request a scratch build of the '
                        'package. Without providing an srpm, it will attempt '
                        'to build the latest commit, which must have been '
                        'pushed. By default all appropriate arches will be '
                        'built.')
        scratch_build_parser.add_argument(
            '--srpm', nargs='?', const='CONSTRUCT',
            help='Build from an srpm. If no srpm is provided with this '
                 'option an srpm will be generated from the current module '
                 'content.')
        scratch_build_parser.set_defaults(command=self.scratch_build)

    def register_sources(self):
        """Register the sources target"""

        sources_parser = self.subparsers.add_parser(
            'sources', help='Download source files',
            description='Download source files')
        sources_parser.add_argument(
            '--outdir', default=os.curdir,
            help='Directory to download files into (defaults to pwd)')
        sources_parser.set_defaults(command=self.sources)

    def register_srpm(self):
        """Register the srpm target"""

        srpm_parser = self.subparsers.add_parser(
            'srpm', help='Create a source rpm',
            parents=[self.rpm_parser_common],
            description='Create a source rpm')
        # optionally define old style hashsums
        srpm_parser.add_argument(
            '--md5', action='store_const', const='md5', default=None,
            dest='hash', help='Use md5 checksums (for older rpm hosts)')
        srpm_parser.set_defaults(command=self.srpm)

    def register_copr_build(self):
        """Register the copr-build target"""

        copr_parser = self.subparsers.add_parser(
            'copr-build', help='Build package in Copr',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent("""
                Build package in Copr.

                Note: you need to have set up correct api key. For more information
                see API KEY section of copr-cli(1) man page.
            """))

        copr_parser.add_argument(
            '--config', required=False,
            metavar='CONFIG', dest='copr_config',
            help="Path to an alternative Copr configuration file")
        copr_parser.add_argument(
            '--nowait', action='store_true', default=False,
            help="Don't wait on build")
        copr_parser.add_argument(
            'project', nargs=1, help='Name of the project in format USER/PROJECT')
        copr_parser.set_defaults(command=self.copr_build)

    def register_switch_branch(self):
        """Register the switch-branch target"""

        switch_branch_parser = self.subparsers.add_parser(
            'switch-branch', help='Work with branches',
            description='This command can switch to a local git branch. If '
                        'provided with a remote branch name that does not '
                        'have a local match it will create one.  It can also '
                        'be used to list the existing local and remote '
                        'branches.')
        switch_branch_parser.add_argument(
            'branch', nargs='?', help='Branch name to switch to')
        switch_branch_parser.add_argument(
            '-l', '--list', action='store_true',
            help='List both remote-tracking branches and local branches')
        switch_branch_parser.add_argument(
            '--fetch', help='Fetch new data from remote before switch',
            action='store_true', dest='fetch')
        switch_branch_parser.set_defaults(command=self.switch_branch)

    def register_tag(self):
        """Register the tag target"""

        tag_parser = self.subparsers.add_parser(
            'tag', help='Management of git tags',
            description='This command uses git to create, list, or delete '
                        'tags.')
        tag_parser.add_argument(
            '-f', '--force', default=False,
            action='store_true', help='Force the creation of the tag')
        tag_parser.add_argument(
            '-m', '--message', default=None,
            help='Use the given <msg> as the tag message')
        tag_parser.add_argument(
            '-c', '--clog', default=False, action='store_true',
            help='Generate the tag message from the spec changelog section')
        tag_parser.add_argument(
            '--raw', action='store_true', default=False,
            help='Make the clog raw')
        tag_parser.add_argument(
            '-F', '--file', default=None,
            help='Take the tag message from the given file')
        tag_parser.add_argument(
            '-l', '--list', default=False, action='store_true',
            help='List all tags with a given pattern, or all if not pattern '
                 'is given')
        tag_parser.add_argument(
            '-d', '--delete', default=False, action='store_true',
            help='Delete a tag')
        tag_parser.add_argument(
            'tag', nargs='?', default=None, help='Name of the tag')
        tag_parser.set_defaults(command=self.tag)

    def register_unused_patches(self):
        """Register the unused-patches target"""

        unused_patches_parser = self.subparsers.add_parser(
            'unused-patches',
            help='Print list of patches not referenced by name in the '
                 'specfile')
        unused_patches_parser.set_defaults(command=self.unused_patches)

    def register_upload(self):
        """Register the upload target"""

        upload_parser = self.subparsers.add_parser(
            'upload', parents=[self.new_sources_parser],
            conflict_handler='resolve',
            help='Upload source files',
            description='This command will upload new source file(s) to '
                        'lookaside cache. Source file names are appended to '
                        'sources file, and .gitignore will be also updated '
                        'with new uploaded file(s). Please remember to commit '
                        'them.')
        upload_parser.set_defaults(command=self.upload, replace=False)

    def register_verify_files(self):
        """Register the verify-files target"""

        verify_files_parser = self.subparsers.add_parser(
            'verify-files', parents=[self.rpm_parser_common],
            help='Locally verify %%files section',
            description="Locally run 'rpmbuild -bl' to verify the spec file's"
                        " %files sections. This requires a successful run of "
                        "'{0} install' in advance.".format(self.name))
        verify_files_parser.set_defaults(command=self.verify_files)

    def register_verrel(self):

        verrel_parser = self.subparsers.add_parser(
            'verrel', help='Print the name-version-release.')
        verrel_parser.set_defaults(command=self.verrel)

    def register_container_build_common(self):
        parser = ArgumentParser(
            'container_build_common', add_help=False, allow_abbrev=False)

        self.container_build_parser_common = parser

        parser.add_argument(
            '--target',
            help='Override the default target',
            default=None)

        parser.add_argument(
            '--nowait',
            action='store_true',
            default=False,
            help="Don't wait on build")

        parser.add_argument(
            '--build-release',
            default=None,
            help="Specify a release value for this build's NVR")

        parser.add_argument(
            '--isolated',
            help='Do not update floating tags in the registry. You must use'
                 ' the --build-release argument',
            action="store_true")

        parser.add_argument(
            '--koji-parent-build',
            default=None,
            help='Specify a Koji NVR for the parent container image. This'
                 ' will override the "FROM" value in your Dockerfile.')

        parser.add_argument(
            '--scratch',
            help='Scratch build',
            action="store_true")

        parser.add_argument(
            '--arches',
            action='append',
            nargs='*',
            help='Limit a scratch or a isolated build to an arch. May have multiple arches.')

        parser.add_argument(
            '--repo-url',
            action='append',
            metavar="URL",
            help='URLs of yum repo files',
            nargs='+')

        parser.add_argument(
            '--signing-intent',
            help="Signing intent of the ODCS composes. If specified, this"
            " must be one of the signing intent names configured on the OSBS"
            " server. If unspecified, the server will use the signing intent"
            " of the compose_ids you specify, or the server's"
            " default_signing_intent. To view the full list of possible"
            " names, see REACTOR_CONFIG in orchestrator.log.")

        parser.add_argument(
            '--skip-remote-rules-validation',
            action='store_true',
            default=False,
            help="Don't check if there's a valid gating.yaml file in the repo")

        parser.add_argument(
            '--skip-build',
            help="Don't create build, but just modify settings for autorebuilds",
            action="store_true")

    def register_container_build(self):
        self.container_build_parser = self.subparsers.add_parser(
            'container-build',
            help='Build a container',
            description='Build a container',
            parents=[self.container_build_parser_common])

        # These arguments are specific to non-Flatpak containers
        #
        # --compose-id is implemented for Flatpaks as a side-effect of the internal
        #      implementation, but it is unlikely to be useful to trigger through rpkg.

        self.container_build_parser.add_argument(
            '--compose-id',
            action='append',
            dest='compose_ids',
            metavar='COMPOSE_ID',
            type=int,
            help='ODCS composes used. Cannot be used with --signing-intent',
            nargs='+')
        self.container_build_parser.add_argument(
            '--replace-dependency',
            action='append',
            metavar="PKG_MANAGER:NAME:VERSION[:NEW_NAME]",
            help='Cachito dependency replacement',
            nargs='+')

        self.container_build_parser.set_defaults(command=self.container_build)

    def register_flatpak_build(self):
        self.flatpak_build_parser = self.subparsers.add_parser(
            'flatpak-build',
            help='Build a Flatpak',
            description='Build a Flatpak',
            parents=[self.container_build_parser_common])

        self.flatpak_build_parser.set_defaults(command=self.flatpak_build)

    def register_container_build_setup(self):
        self.container_build_setup_parser = \
            self.subparsers.add_parser('container-build-setup',
                                       help='set options for container-build')
        group = self.container_build_setup_parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--get-autorebuild',
            help='Get autorebuild value',
            action='store_true',
            default=None)
        group.add_argument(
            '--set-autorebuild',
            help='Turn autorebuilds on/off',
            choices=('true', 'false'),
            default=None)
        self.container_build_setup_parser.set_defaults(
            command=self.container_build_setup)

    # All the command functions go here
    def usage(self):
        self.parser.print_help()

    def _upload_file_for_build(self, file, name=None):
        """Upload a file (srpm or module) for building.

        :param str file: specify which file to upload.
        :param str name: specify alternate basename for file on upload server
        :return: a unique path of directory inside server into which the file
            has been uploaded.
        :rtype: str
        """
        # Figure out if we want a verbose output or not
        callback = None
        if not self.args.q:
            callback = koji_cli.lib._progress_callback
        # Define a unique path for this upload. Learned from koji to use prefix
        # cli-build.
        uniquepath = koji_cli.lib.unique_path('cli-build')
        if not name:
            name = os.path.basename(file)
        # Should have a try here, not sure what errors we'll get yet though
        if self.args.dry_run:
            self.log.info('DRY-RUN: self.cmd.koji_upload(%s, %s, name=%s, callback=%s)',
                          file, uniquepath, name, callback)
        else:
            self.cmd.koji_upload(file, uniquepath, name=name, callback=callback)
        if not self.args.q:
            # print an extra blank line due to callback oddity
            print('')
        return '%s/%s' % (uniquepath, name)

    def _get_rpm_package_name(self, rpm_file):
        """Returns rpm package name by examining rpm file

        :param str rpm_file: specify path to RPM file.
        :return: the name of the package in the specified file according to
            the contained RPM header information, or None if file does not
            contain RPM data.
        :rtype: str
        """

        def _string(s):
            """RPM 4.15 changed header returns from type 'bytes' to 'string'.
            Handle either by always returning 'string'.

            :param s: a 'bytes' or 'string' value representing an RPM
                package header.
            :return: always a 'string' representation of the RPM header.
            :rtype: str
            """
            if isinstance(s, bytes):
                return s.decode('utf-8')
            return s

        ts = rpm.TransactionSet()
        ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
        fdno = os.open(rpm_file, os.O_RDONLY)
        try:
            hdr = ts.hdrFromFdno(fdno)
        except rpm.error:
            return None
        os.close(fdno)
        return _string(hdr[rpm.RPMTAG_NAME])

    def _handle_srpm_option(self):
        """Generate SRPM according to --srpm option value and upload it

        :return: a unique path of directory inside server into which the SRPM
            will be uploaded. If --srpm is not specified, no SRPM will be
            uploaded and None is returned.
        :rtype: str
        """
        if hasattr(self.args, 'srpm') and self.args.srpm:
            # See if we need to generate the srpm first
            if self.args.srpm == 'CONSTRUCT':
                self.log.debug('Generating an srpm')
                self.srpm()
                self.args.srpm = '%s.src.rpm' % self.cmd.nvr
            return self._upload_file_for_build(self.args.srpm)

    def _watch_build_tasks(self, task_ids):
        """Watch build tasks

        If --nowait is specified, it does not start to watch.

        :param list task_ids: a list of task IDs to watch.
        """
        if self.args.nowait:
            return
        # Pass info off to our koji task watcher
        if self.args.dry_run:
            self.log.info('DRY-RUN: Watch tasks: %s', task_ids)
        else:
            return koji_cli.lib.watch_tasks(
                self.cmd.kojisession,
                task_ids,
                ki_handler=utils.make_koji_watch_tasks_handler(self.cmd.build_client)
            )

    def extract_greenwave_url(self):
        greenwave_url = None
        if not self.args.skip_remote_rules_validation:
            section_name = "%s.greenwave" % self.name
            if self.config.has_option(section_name, 'url'):
                greenwave_url = self.config.get(section_name, 'url')
        return greenwave_url

    def greenwave_validation_gating(self, greenwave_url, data):
        response = requests.post(
                "%s/%s" % (greenwave_url, 'api/v1.0/validate-gating-yaml'),
                data=data,
                timeout=30)
        return response

    def check_remote_rules_gating(self):
        # checking if there is a file gating.yaml in the repo working tree
        # with additional policies for the greenwave feature RemoteRule
        greenwave_url = self.extract_greenwave_url()
        filename = os.path.join(self.args.path, 'gating.yaml')
        if (self.args.skip_remote_rules_validation or
                not os.path.exists(filename) or
                not greenwave_url or self.args.scratch):
            return

        # read content from gating.yaml and validate it from greenwave endpoint
        with open(filename, 'rb') as gating_file:
            response = self.greenwave_validation_gating(
                greenwave_url, gating_file.read())
            resp_msg = response.json()['message']

            if response.status_code == 400:
                raise rpkgError(
                    'Found a gating.yaml file in your repo with additional '
                    'Greenwave policies, but it is not valid.\n'
                    'Please fix the file or skip this check using the '
                    'option --skip-remote-rules-validation.\n'
                    'Error response from Greenwave: %s' % resp_msg)
            elif response.status_code != 200:
                raise rpkgError(
                    'Found a gating.yaml file in your repo with additional '
                    'Greenwave policies, but it was not possible to validate '
                    'it for an unknown problem.\n'
                    'It is possible to skip this check using the option '
                    '--skip-remote-rules-validation.\n'
                    'Error response from Greenwave: %s' % resp_msg)
            else:
                self.log.info(("Found a gating.yaml file in the repo and it is properly "
                               "configured"))

    def build(self, sets=None):
        """Implement build command"""
        self.check_remote_rules_gating()

        try:
            task_id = self._build(sets=sets)
        finally:
            self.log.debug('Logout kojisession')
            self.cmd.kojisession.logout()

        if isinstance(task_id, int):
            task_ids = [task_id]
        else:
            task_ids = task_id

        return self._watch_build_tasks(task_ids)

    def _build(self, sets=None):
        """Interface for build, scratch-build and chainbuild to start build

        This is where to add general code for all the build commands.

        :params bool sets: used for ``chainbuild`` to indicate if packages in
            the chain are separated into groups in which packages will be built
            in parallel. For ``build`` and ``scratch-build``, no need to pass
            any value and just keep it None.
        :return: task ID returned from build system. In some cases, the
            overrided ``_build`` could return a list of task IDs as well.
        :rtype: int or list[int]
        """
        # We may have gotten arches by way of scratch build, so handle them
        arches = None
        if hasattr(self.args, 'arches'):
            arches = self.args.arches

        # See if this is a chain or not
        chain = None
        if hasattr(self.args, 'chain'):
            chain = self.args.chain

        # nvr_check option isn't set by all commands which calls this
        # function so handle it as an optional argument
        nvr_check = True
        if hasattr(self.args, 'nvr_check'):
            nvr_check = self.args.nvr_check

        # Need to do something with BUILD_FLAGS or KOJI_FLAGS here for compat
        if self.args.target:
            self.cmd.target = self.args.target

        # handle uploading the srpm if we got one
        url = self._handle_srpm_option()

        return self.cmd.build(
            skip_tag=self.args.skip_tag,
            scratch=self.args.scratch,
            background=self.args.background,
            url=url,
            chain=chain,
            arches=arches,
            sets=sets,
            nvr_check=nvr_check,
            fail_fast=self.args.fail_fast)

    def chainbuild(self):
        """Implement chain-build command"""
        if self.cmd.repo_name in self.args.package:
            raise Exception('%s must not be in the chain' % self.cmd.repo_name)

        # make sure we didn't get an empty chain
        if self.args.package == [':']:
            raise Exception('Must provide at least one dependency build')

        # Break the chain up into sections
        sets = False
        urls = []
        build_set = []
        self.log.debug('Processing chain %s', ' '.join(self.args.package))
        for component in self.args.package:
            if component == ':':
                # We've hit the end of a set, add the set as a unit to the
                # url list and reset the build_set.
                urls.append(build_set)
                self.log.debug('Created a build set: %s', ' '.join(build_set))
                build_set = []
                sets = True
            else:
                # Figure out the scm url to build from package name
                hash = self.cmd.get_latest_commit(component,
                                                  self.cmd.branch_merge)
                # Passing given package name to module_name parameter directly
                # without guessing namespace as no way to guess that. rpms/
                # will be added by default if namespace is not given.
                url = self.cmd.construct_build_url(component, hash)
                # If there are no ':' in the chain list, treat each object as
                # an individual chain
                if ':' in self.args.package:
                    build_set.append(url)
                else:
                    urls.append([url])
                    self.log.debug('Created a build set: %s', url)
        # Take care of the last build set if we have one
        if build_set:
            self.log.debug('Created a build set: %s', ' '.join(build_set))
            urls.append(build_set)
        # See if we ended in a : making our last build it's own group
        if self.args.package[-1] == ':':
            self.log.debug('Making the last build its own set.')
            urls.append([])
        # pass it off to build
        self.args.chain = urls
        self.args.skip_tag = False
        self.args.scratch = False
        return self.build(sets)

    def clean(self):
        dry = False
        useignore = True
        if self.args.dry_run:
            dry = True
        if self.args.x:
            useignore = False
        return self.cmd.clean(dry, useignore)

    def clog(self):
        self.cmd.clog(raw=self.args.raw)

    def clone(self):
        # corrects user-given wrong format of a repo name
        if self.args.repo[0].endswith('.git'):
            repo = self.args.repo[0][:-4]
            self.log.warn("Repo name should't contain '.git' suffix. "
                          "Correcting the repo name: '%s'" % repo)

        if self.args.branches:
            self.cmd.clone_with_dirs(self.args.repo[0],
                                     anon=self.args.anonymous,
                                     target=self.args.clone_target,
                                     depth=self.args.depth,
                                     extra_args=self.extra_args)
        else:
            self.cmd.clone(self.args.repo[0],
                           branch=self.args.branch,
                           anon=self.args.anonymous,
                           target=self.args.clone_target,
                           depth=self.args.depth,
                           extra_args=self.extra_args)

    def commit(self):
        if self.args.with_changelog and not self.args.message:
            raise rpkgError('--with-changelog must be used with -m together.')

        if self.args.clog or (self.args.message and self.args.with_changelog):
            self.cmd.clog(raw=self.args.raw, subject=self.args.message)
            # This assignment is a magic because commit message is in the file
            # commit-message already.
            self.args.message = None
            self.args.file = os.path.abspath(os.path.join(self.args.path, 'clog'))

        # It is okay without specifying either -m or --clog. Changes will be
        # committed with command ``git commit``, then git will invoke default
        # configured editor for you and let you enter the commit message.

        try:
            self.cmd.commit(self.args.message, self.args.file, self.args.files, self.args.signoff)
            if self.args.tag:
                tagname = self.cmd.nvr
                self.cmd.add_tag(tagname, True, self.args.message, self.args.file)
        except Exception:
            if self.args.tag:
                self.log.error('Could not commit, will not tag!')
            if self.args.push:
                self.log.error('Could not commit, will not push!')
            raise
        finally:
            if self.args.clog or self.args.with_changelog and os.path.isfile(self.args.file):
                os.remove(self.args.file)
                del self.args.file

        if self.args.push:
            self.push()

    def compile(self):
        self.sources()
        self.cmd.compile(builddir=self.args.builddir,
                         arch=self.args.arch,
                         define=self.args.define,
                         extra_args=self.extra_args,
                         short=self.args.short_circuit,
                         nocheck=self.args.nocheck,)

    def container_build_koji(self):
        # Keep it around for backward compatibility
        self.container_build()

    def container_build(self, flatpak=False):
        target_override = False
        # Override the target if we were supplied one
        if self.args.target:
            self.cmd._target = self.args.target
            target_override = True

        # Group similar argparse arguments into single list
        def group_arguments(arg):
            return sum((item for item in arg), [])

        if self.args.repo_url:
            self.args.repo_url = group_arguments(self.args.repo_url)

        if self.args.arches:
            self.args.arches = group_arguments(self.args.arches)

        if self.args.release:
            self.log.warning('using --release with container-build will cause git_branch to be '
                             'overridden, and if the specified commit is not present in the '
                             'overridden branch, the build will fail.  Use --target to avoid '
                             'this behavior')

        opts = {"scratch": self.args.scratch,
                "quiet": self.args.q,
                "release": self.args.build_release,
                "isolated": self.args.isolated,
                "koji_parent_build": self.args.koji_parent_build,
                "git_branch": self.cmd.branch_merge,
                "arches": self.args.arches,
                "signing_intent": self.args.signing_intent,
                "skip_build": self.args.skip_build,
                "yum_repourls": self.args.repo_url}

        if not flatpak:
            if self.args.compose_ids:
                self.args.compose_ids = group_arguments(self.args.compose_ids)

            if self.args.replace_dependency:
                self.args.replace_dependency = group_arguments(self.args.replace_dependency)

            if self.args.compose_ids and self.args.signing_intent:
                raise rpkgError("argument --compose-id: not allowed with argument"
                                " --signing-intent")
            opts.update({
                "dependency_replacements": self.args.replace_dependency,
                "compose_ids": self.args.compose_ids,
            })

        if self.args.isolated and not self.args.build_release:
            self.container_build_parser.error(
                'missing --build-release: using --isolated requires'
                ' --build-release option')

        section_name = "%s.container-build" % self.name
        err_msg = "Missing %(option)s option in [%(plugin.section)s] section. " \
                  "Using %(option)s from [%(root.section)s]"
        err_args = {"plugin.section": section_name, "root.section": self.name}

        kojiprofile = None
        if self.config.has_option(section_name, "kojiprofile"):
            kojiprofile = self.config.get(section_name, "kojiprofile")
        else:
            err_args["option"] = "kojiprofile"
            self.log.debug(err_msg % err_args)
            kojiprofile = self.config.get(self.name, "kojiprofile")

        if self.config.has_option(section_name, "build_client"):
            build_client = self.config.get(section_name, "build_client")
        else:
            err_args["option"] = "build_client"
            self.log.debug(err_msg % err_args)
            build_client = self.config.get(self.name, "build_client")

        self.check_remote_rules_gating()

        # We use MBS to find information about the module to build into a Flatpak
        if flatpak:
            self.set_module_api_url()

        rv = self.cmd.container_build_koji(
            target_override,
            opts=opts,
            kojiprofile=kojiprofile,
            build_client=build_client,
            koji_task_watcher=koji_cli.lib.watch_tasks,
            nowait=self.args.nowait,
            flatpak=flatpak)
        return rv

    def flatpak_build(self):
        self.container_build(flatpak=True)

    def container_build_setup(self):
        self.cmd.container_build_setup(get_autorebuild=self.args.get_autorebuild,
                                       set_autorebuild=self.args.set_autorebuild)

    def copr_build(self):
        self.log.debug('Generating an srpm')
        self.args.hash = None
        self.srpm()
        srpm_name = '%s.src.rpm' % self.cmd.nvr
        self.cmd.copr_build(self.args.project[0],
                            srpm_name,
                            self.args.nowait,
                            self.args.copr_config)

    def diff(self):
        self.cmd.diff(self.args.cached, self.args.files)

    def gimmespec(self):
        print(self.cmd.spec)

    def gitbuildhash(self):
        print(self.cmd.gitbuildhash(self.args.build))

    def giturl(self):
        print(self.cmd.giturl())

    def import_srpm(self):
        uploadfiles = self.cmd.import_srpm(self.args.srpm)
        if uploadfiles:
            self.cmd.upload(uploadfiles, replace=True, offline=self.args.offline)
        if not self.args.skip_diffs:
            self.cmd.diff(cached=True)
        self.log.info('--------------------------------------------')
        if uploadfiles and self.args.offline:
            self.log.info("New content staged without uploading sources.")
            self.log.info("Commit and upload (%s upload <source>) if happy or revert with: "
                          "'git reset --hard HEAD' (warning: it reverts also eventual user "
                          "changes)." % (self._name,))
        else:
            self.log.info("New content staged and new sources uploaded.")
            self.log.info("Commit if happy or revert with: 'git reset --hard HEAD' (warning: "
                          "it reverts also eventual user changes).")

    def install(self):
        self.sources()
        self.cmd.install(builddir=self.args.builddir,
                         arch=self.args.arch,
                         define=self.args.define,
                         extra_args=self.extra_args,
                         short=self.args.short_circuit,
                         nocheck=self.args.nocheck,
                         buildrootdir=self.args.buildrootdir,)

    def lint(self):
        self.cmd.lint(self.args.info, self.args.rpmlintconf)

    def list_side_tags(self):
        user = self.args.tag_owner or (self.user if self.args.mine else None)
        tags = self.cmd.list_side_tags(base_tag=self.args.base_tag, user=user)
        for tag in sorted(tags, key=lambda t: t["name"]):
            print("%(name)s\t(id %(id)d)\t(user %(user_name)s|%(user_id)s)" % tag)

    def local(self):
        self.sources()

        localargs = []

        if self.args.bcond_with:
            for arg in self.args.bcond_with:
                localargs.extend(['--with', arg])

        if self.args.bcond_without:
            for arg in self.args.bcond_without:
                localargs.extend(['--without', arg])

        self.cmd.local(localargs,
                       builddir=self.args.builddir,
                       arch=self.args.arch,
                       define=self.args.define,
                       extra_args=self.extra_args,
                       buildrootdir=self.args.buildrootdir,
                       hashtype=self.args.hash,)

    def mockbuild(self):
        try:
            self.sources()
        except Exception as e:
            raise rpkgError('Could not download sources: %s', e)

        mockargs = []

        if self.args.no_clean or self.args.no_clean_all:
            mockargs.append('--no-clean')

        if self.args.no_cleanup_after or self.args.no_clean_all:
            mockargs.append('--no-cleanup-after')

        if self.args.bcond_with:
            for arg in self.args.bcond_with:
                mockargs.extend(['--with', arg])

        if self.args.bcond_without:
            for arg in self.args.bcond_without:
                mockargs.extend(['--without', arg])

        if self.args.enablerepo:
            for repo_value in self.args.enablerepo:
                mockargs.extend(['--enablerepo', repo_value])

        if self.args.disablerepo:
            for repo_value in self.args.disablerepo:
                mockargs.extend(['--disablerepo', repo_value])

        if self.args.enable_network:
            mockargs.append('--enable-network')

        if self.extra_args:
            mockargs.extend(self.extra_args)
            self.log.debug("Extra args '{0}' are passed to mock "
                           "command".format(self.extra_args))

        # Pick up any mockargs from the env
        try:
            mockargs += os.environ['MOCKARGS'].split()
        except KeyError:
            # there were no args
            pass
        try:
            self.cmd.mockbuild(mockargs, self.args.root,
                               hashtype=self.args.hash,
                               shell=self.args.shell)
        except Exception as e:
            raise rpkgError(e)

    def mock_config(self):
        print(self.cmd.mock_config(self.args.target, self.args.arch))

    def module_build(self):
        """Builds a module using MBS"""
        self.set_module_api_url()
        self.module_validate_config()

        modmd_path = None
        srpm_links = []
        if self.args.file_path or self.args.srpms:
            if not self.args.scratch:
                raise rpkgError('--file and --srpms may only be used with '
                                'scratch module builds.')
            if self.args.file_path:
                modmd_path = os.path.abspath(self.args.file_path)
                if not os.path.isfile(modmd_path):
                    raise IOError("Module metadata yaml file %s not found!" % modmd_path)
            if self.args.srpms:
                for srpm in self.args.srpms:
                    srpm_path = os.path.abspath(srpm)
                    if not os.path.isfile(srpm_path):
                        raise IOError("SRPM file %s not found!" % srpm_path)
                    srpm_name = "%s.src.rpm" % self._get_rpm_package_name(srpm_path)
                    srpm_links.append(
                        self._upload_file_for_build(os.path.abspath(srpm_path),
                                                    name=srpm_name))

        scm_url = None
        branch = None
        try:
            scm_url, branch = self.cmd.module_get_scm_info(
                self.args.scm_url, self.args.branch)
        except rpkgError as e:
            # if a scratch build modulemd was specified on the command line,
            # it's OK if the SCM info can't be determined
            if not modmd_path:
                raise(e)

        auth_method, oidc_id_provider, oidc_client_id, oidc_client_secret, \
            oidc_scopes = self.module_get_auth_config()

        if not self.args.q:
            print('Submitting the module build...')
        build_ids = self._cmd.module_submit_build(
            scm_url, branch, auth_method, self.args.buildrequires, self.args.requires,
            self.args.optional, oidc_id_provider, oidc_client_id,
            oidc_client_secret, oidc_scopes,
            self.args.scratch, modmd_path, srpm_links)
        if self.args.watch:
            try:
                self.module_watch_build(build_ids)
            except KeyboardInterrupt:
                print('And now your watch is ended. Use module-build-watch command to watch again.')
                raise
        elif not self.args.q:
            if len(build_ids) > 1:
                ids_to_print = 'builds {0} and {1} were'.format(
                    ', '.join([str(b_id) for b_id in build_ids[0:-1]]),
                    str(build_ids[-1]))
            else:
                ids_to_print = 'build {0} was'.format(str(build_ids[0]))
            print('The {0} submitted to the MBS' .format(ids_to_print))
            print('Build URLs:')
            for build_id in build_ids:
                print(self.cmd.module_get_url(build_id, verbose=False))

    def module_build_cancel(self):
        """Cancel an MBS build"""
        self.set_module_api_url()
        build_id = self.args.build_id
        auth_method, oidc_id_provider, oidc_client_id, oidc_client_secret, \
            oidc_scopes = self.module_get_auth_config()

        if not self.args.q:
            print('Cancelling module build #{0}...'.format(build_id))
        self.cmd.module_build_cancel(
            build_id, auth_method, oidc_id_provider, oidc_client_id,
            oidc_client_secret, oidc_scopes)
        if not self.args.q:
            print('The module build #{0} was cancelled'.format(build_id))

    def module_build_info(self):
        """Show information about an MBS build"""
        self.set_module_api_url()
        self.cmd.module_build_info(self.args.build_id)

    def module_build_local(self):
        """Build a module locally using mbs-manager"""
        self.module_validate_config()

        if not self.args.stream:
            _, stream = self.cmd.module_get_scm_info(check_repo=False)
        else:
            stream = self.args.stream

        if not self.args.file_path:
            file_path = os.path.join(self.cmd.path, self.cmd.repo_name + ".yaml")
        else:
            file_path = self.args.file_path

        if self.args.srpms:
            for srpm in self.args.srpms:
                if not os.path.isfile(srpm):
                    raise IOError("SRPM file %s not found!" % srpm)

        if not os.path.isfile(file_path):
            raise IOError("Module metadata yaml file %s not found!" % file_path)

        config_section = '{0}.mbs'.format(self.name)
        mbs_config = None
        if self.config.has_option(config_section, 'config_file'):
            mbs_config = self.config.get(config_section, 'config_file')
        mbs_config_section = None
        if self.config.has_option(config_section, 'config_section'):
            mbs_config_section = self.config.get(config_section, 'config_section')

        self.cmd.module_local_build(
            file_path, stream, self.args.local_builds_nsvs,
            verbose=self.args.v, debug=self.args.debug, skip_tests=self.args.skiptests,
            mbs_config=mbs_config, mbs_config_section=mbs_config_section,
            default_streams=self.args.default_streams,
            offline=self.args.offline,
            base_module_repositories=self.args.base_module_repositories,
            srpms=self.args.srpms)

    def module_get_auth_config(self):
        """Get the authentication configuration for the MBS

        :return: a tuple consisting of the authentication method, the OIDC ID
            provider, the OIDC client ID, the OIDC client secret, and the OIDC
            scopes. If the authentication method is not OIDC, the OIDC values
            in the tuple are set to None.
        :rtype: tuple
        """
        auth_method = self.config.get(self.config_section, 'auth_method')
        oidc_id_provider = None
        oidc_client_id = None
        oidc_client_secret = None
        oidc_scopes = None
        if auth_method == 'oidc':
            oidc_id_provider = self.config.get(
                self.config_section, 'oidc_id_provider')
            oidc_client_id = self.config.get(
                self.config_section, 'oidc_client_id')
            oidc_scopes_str = self.config.get(
                self.config_section, 'oidc_scopes')
            oidc_scopes = [
                scope.strip() for scope in oidc_scopes_str.split(',')]
            if self.config.has_option(self.config_section,
                                      'oidc_client_secret'):
                oidc_client_secret = self.config.get(
                    self.config_section, 'oidc_client_secret')
        return (auth_method, oidc_id_provider, oidc_client_id,
                oidc_client_secret, oidc_scopes)

    @property
    def module_api_version(self):
        """
        A property that returns that maximum API version supported by both
        rpkg and MBS
        :return: an int of the API version
        """
        if self._module_api_version is None:
            self.module_validate_config()
            api_url = self.config.get(self.config_section, 'api_url')
            # Eventually, tools built with rpkg should have their configuration
            # updated to not hardcode the MBS API version. This checks if it is
            # hardcoded.
            if not re.match(r'^.+/\d+/$', api_url):
                # The API version is not hardcoded, so let's query using the v1
                # API to find out the API versions that MBS supports.
                api_url = '{0}/1/'.format(api_url.rstrip('/'))
            self._module_api_version = self.cmd.module_get_api_version(api_url)
        return self._module_api_version

    @property
    def module_api_url(self):
        """
        A property that returns the MBS base API URL based on the maximum API
        version supported by both rpkg and MBS
        :return: a string of the MBS API URL
        """
        if self._module_api_url:
            return self._module_api_url
        # Calling this now will ensure that self.module_validate_config()
        # has been run
        api_version = self.module_api_version
        api_url = self.config.get(self.config_section, 'api_url')
        # Eventually, tools built with rpkg should have their configuration
        # updated to not hardcode the MBS API version. This checks if it is
        # hardcoded.
        if re.match(r'.+/\d+/$', api_url):
            self._module_api_url = re.sub(
                r'/\d+/$', '/{0}/'.format(str(api_version)), api_url)
        else:
            # The API version is not hardcoded, so we can simply add on the
            # API version we want to use
            self._module_api_url = '{0}/{1}/'.format(
                api_url.rstrip('/'), api_version)
        return self._module_api_url

    def set_module_api_url(self):
        self.cmd.module_api_url = self.module_api_url

    def module_build_watch(self):
        """Watch MBS builds from the command-line"""
        self.module_watch_build(self.args.build_id)

    def module_overview(self):
        """Show the overview of the latest builds in the MBS"""
        self.set_module_api_url()
        owner = self.args.owner
        if self.args.mine:
            owner = self.cmd.user
            if not owner:
                raise rpkgError("Can not obtain current Kerberos name or username")
        self.cmd.module_overview(
            self.args.limit,
            finished=(not self.args.unfinished),
            owner=owner)

    def module_scratch_build(self):
        # A module scratch build is just a module build with --scratch
        self.args.scratch = True
        return self.module_build()

    def module_validate_config(self):
        """Validates the configuration needed for MBS commands

        :raises: :py:exc:`pyrpkg.errors.rpkgError`
        """
        self.config_section = '{0}.mbs'.format(self.name)
        # Verify that all necessary config options are set
        config_error = ('The config option "{0}" in the "{1}" section is '
                        'required')
        if not self.config.has_option(self.config_section, 'auth_method'):
            raise rpkgError(config_error.format(
                'auth_method', self.config_section))
        required_configs = ['api_url']
        auth_method = self.config.get(self.config_section, 'auth_method')
        if auth_method not in ['oidc', 'kerberos']:
            raise rpkgError('The MBS authentication mechanism of "{0}" is not '
                            'supported'.format(auth_method))

        if auth_method == 'oidc':
            # Try to import this now so the user gets immediate feedback if
            # it isn't installed
            try:
                import openidc_client  # noqa: F401
            except ImportError:
                raise rpkgError('python-openidc-client needs to be installed')
            required_configs.append('oidc_id_provider')
            required_configs.append('oidc_client_id')
            required_configs.append('oidc_scopes')
        elif auth_method == 'kerberos':
            # Try to import this now so the user gets immediate feedback if
            # it isn't installed
            try:
                import requests_kerberos  # noqa: F401
            except ImportError:
                raise rpkgError(
                    'python-requests-kerberos needs to be installed')

        for required_config in required_configs:
            if not self.config.has_option(self.config_section,
                                          required_config):
                raise rpkgError(config_error.format(
                    required_config, self.config_section))

    def module_watch_build(self, build_ids):
        """
        Watches the first MBS build in the list in a loop that updates every
        15 seconds. The loop ends when the build state is 'failed', 'done', or
        'ready'.

        :param build_ids: a list of module build IDs
        :type build_ids: list[int]
        """
        self.set_module_api_url()
        self.cmd.module_watch_build(build_ids)

    def new(self):
        new_diff = self.cmd.new()
        # When running rpkg with old version GitPython<1.0 which returns string
        # in type basestring, no need to encode.
        if isinstance(new_diff, six.string_types):
            print(new_diff)
        else:
            print(new_diff.encode('utf-8'))

    def new_sources(self):
        # Check to see if the files passed exist
        for file in self.args.files:
            if not os.path.isfile(file):
                raise Exception('Path does not exist or is '
                                'not a file: %s' % file)
        try:
            self.cmd.upload(
                self.args.files,
                replace=self.args.replace,
                offline=self.args.offline,)
        except AlreadyUploadedError:
            self.log.info("All sources were already uploaded.")
        else:
            self.log.info("Source upload succeeded. Don't forget to commit the "
                          "sources file")

    def upload(self):
        self.new_sources()

    def patch(self):
        self.cmd.patch(self.args.suffix, rediff=self.args.rediff)

    def prep(self):
        self.sources()
        self.cmd.prep(builddir=self.args.builddir,
                      arch=self.args.arch,
                      define=self.args.define,
                      extra_args=self.extra_args,
                      buildrootdir=self.args.buildrootdir,)

    def pull(self):
        self.cmd.pull(rebase=self.args.rebase,
                      norebase=self.args.no_rebase)

    def push(self):
        if not self.oidc_configured:
            extra_config = {}
        else:
            extra_config = {
                'credential.helper': ' '.join(utils.find_me() + ['gitcred']),
                'credential.useHttpPath': 'true'}
        self.cmd.push(getattr(self.args, 'force', False), extra_config)

    def remote(self):
        """Handle command remote"""
        # will be in self.args by default if not user specified by the
        # --remote-name flag.
        if ("remote_name" in vars(self.args)):
            self.cmd.remote(self.args.remote_name,  # name for remote
                            self.args.repo_name)  # name of package;
        else:
            # not overloading the function of "<> remote",
            # expecting that this will show the current remotes.
            self.cmd._run_command(["git", "remote", "-v"])

    def remove_side_tag(self):
        self.cmd.remove_side_tag(self.args.TAG)
        print("Tag deleted.")

    def request_side_tag(self):
        tag_info = self.cmd.request_side_tag(
            base_tag=self.args.base_tag, suffix=self.args.suffix
        )
        print("Side tag '%(name)s' (id %(id)d) created." % tag_info)
        print("Use '%s build --target=%s' to use it." % (self.name, tag_info["name"]))
        print(
            "Use '%s wait-repo %s' to wait for the build repo to be generated."
            % (self.cmd.build_client, tag_info["name"])
        )

    def retire(self):
        # Skip if package/module is already retired...
        marker = self.cmd.is_retired()
        # marker is file that indicates retirement
        if marker:
            self.log.warn('{0} found, package or module is already retired. '
                          'Will not remove files from git or overwrite '
                          'existing {0} file.'.format(marker))
            return 1
        else:
            self.cmd.retire(self.args.reason)
            self.push()

    def scratch_build(self):
        # A scratch build is just a build with --scratch
        self.args.scratch = True
        self.args.skip_tag = False
        return self.build()

    def sources(self):
        """Download files listed in sources

        For command compile, prep, install, local and srpm, files are needed to
        be downloaded before doing what the command does. Hence, for these
        cases, sources is not called from command line. Instead, from rpkg
        inside.
        """
        # When sources is not called from command line, option outdir is not
        # available.
        outdir = getattr(self.args, 'outdir', None)
        self.cmd.sources(outdir)

    def srpm(self):
        self.sources()

        # Koji does not allow defines, custom builddir and custom buildroot.
        # Argparse won't set them for koji style builds. Normal koji builds
        # are for all arches and not set via argparse.
        self.cmd.srpm(
            builddir=getattr(self.args, 'builddir', None),
            arch=getattr(self.args, 'arch', None),
            define=getattr(self.args, 'define', None),
            extra_args=self.extra_args,
            buildrootdir=getattr(self.args, 'buildrootdir', None),
            hashtype=self.args.hash,)

    def switch_branch(self):
        if self.args.branch:
            self.cmd.switch_branch(self.args.branch, self.args.fetch)
        else:
            (locals, remotes) = self.cmd._list_branches(self.args.fetch)
            # This is some ugly stuff here, but trying to emulate
            # the way git branch looks
            locals = ['  %s  ' % branch for branch in locals]
            local_branch = self.cmd.repo.active_branch.name
            locals[locals.index('  %s  ' %
                                local_branch)] = '* %s' % local_branch
            print('Locals:\n%s\nRemotes:\n  %s' %
                  ('\n'.join(locals), '\n  '.join(remotes)))

    def tag(self):
        if self.args.list:
            self.cmd.list_tag(self.args.tag)
        elif self.args.delete:
            self.cmd.delete_tag(self.args.tag)
        else:
            filename = self.args.file
            tagname = self.args.tag
            if not tagname or self.args.clog:
                if not tagname:
                    tagname = self.cmd.nvr
                if self.args.clog:
                    self.cmd.clog(self.args.raw)
                    filename = 'clog'
            self.cmd.add_tag(tagname, self.args.force,
                             self.args.message, filename)

    def unused_patches(self):
        unused = self.cmd.unused_patches()
        print('\n'.join(unused))

    def verify_files(self):
        self.cmd.verify_files(builddir=self.args.builddir,
                              define=self.args.define,
                              extra_args=self.extra_args,
                              buildrootdir=self.args.buildrootdir)

    def verrel(self):
        print('%s-%s-%s' % (self.cmd.repo_name, self.cmd.ver,
                            self.cmd.rel))

    # Stole these three functions from /usr/bin/koji
    def setupLogging(self, log):
        """Setup the various logging stuff."""

        # Assign the log object to self
        self.log = log

        # Add a log filter class
        class StdoutFilter(logging.Filter):

            def filter(self, record):
                # If the record level is 20 (INFO) or lower, let it through
                return record.levelno <= logging.INFO

        # have to create a filter for the stdout stream to filter out WARN+
        myfilt = StdoutFilter()
        # Simple format
        formatter = logging.Formatter('%(message)s')
        stdouthandler = logging.StreamHandler(sys.stdout)
        stdouthandler.addFilter(myfilt)
        stdouthandler.setFormatter(formatter)
        stderrhandler = logging.StreamHandler()
        stderrhandler.setLevel(logging.WARNING)
        stderrhandler.setFormatter(formatter)
        self.log.addHandler(stdouthandler)
        self.log.addHandler(stderrhandler)

    def parse_cmdline(self, manpage=False):
        """Parse the commandline, optionally make a manpage

        This also sets up self.user
        """

        if manpage:
            # Generate the man page
            man_name = self.name
            if man_name.endswith('.py'):
                man_name = man_name[:-3]
            man_page = __import__('%s' % man_name)
            man_page.generate(self.parser, self.subparsers)
            sys.exit(0)
            # no return possible

        # initialize bash autocompletion
        if argcomplete is not None:
            argcomplete.autocomplete(self.parser)
        # Parse the args
        # There are two groups of arguments:
        # * standard arguments defined by individual parsers
        # * extra arguments that are relevant for some (individually allowed)
        #   commands. They are passed to underlying command (usually appended
        #   to the rest of arguments on commandline)

        argv = sys.argv[1:]
        if "--" in argv:
            i = argv.index("--")
            self.args = self.parser.parse_args(argv[:i])
            self.extra_args = argv[i+1:]
        else:
            self.args = self.parser.parse_args()
            self.extra_args = getattr(self.args, 'extra_args', None)
            if self.extra_args:
                print("Warning: extra_args in the command are not separated "
                      "with '--'. It might not work correctly.\n",
                      file=sys.stderr)

        # This is due to a difference argparse behavior to Python 2 version.
        # In Python 3, argparse will proceed to here without reporting
        # "too few arguments". Instead, self.args does not have attribute
        # command.
        if not hasattr(self.args, 'command'):
            self.parser.print_help()
            sys.exit(1)

        if not self.args.repo_name and self.args.repo_namespace:
            self.parser.error(
                'missing --name: using --namespace requires --name option')

        if self.args.repo_namespace:
            if self.config.has_option(self.name, 'distgit_namespaces'):
                namespaces = self.config.get(
                    self.name, 'distgit_namespaces').split()
                if self.args.repo_namespace not in namespaces:
                    self.parser.error('namespace {0} is not valid'.format(
                        self.args.repo_namespace))

        if self.args.user:
            self.user = self.args.user
        else:
            self.user = getpass.getuser()
