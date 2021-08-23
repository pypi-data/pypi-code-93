# pyrpkg - a Python library for RPM Packagers
#
# Copyright (C) 2011 Red Hat Inc.
# Author(s): Jesse Keating <jkeating@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

from __future__ import print_function

import errno
import fnmatch
import getpass
import glob
import io
import json
import logging
import os
import posixpath
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from itertools import groupby
from multiprocessing.dummy import Pool as ThreadPool
from operator import itemgetter

import cccolutils
import git
import koji
import requests
import rpm
import six
import yaml
from six.moves import configparser, urllib
from six.moves.urllib.parse import urljoin

from pyrpkg import layout
from pyrpkg.errors import (AlreadyUploadedError, HashtypeMixingError,
                           UnknownTargetError, rpkgAuthError, rpkgError)
from pyrpkg.lookaside import CGILookasideCache
from pyrpkg.sources import SourcesFile
from pyrpkg.spec import SpecFile
from pyrpkg.utils import (cached_property, extract_srpm, find_me,
                          is_file_tracked, is_lookaside_eligible_file,
                          log_result)

from .gitignore import GitIgnore

# libmodulemd might not be available for some platforms
# currently python27 and older versions are missing
try:
    import gi
    gi.require_version("Modulemd", "2.0")  # raises ValueError
    from gi.repository import Modulemd  # noqa
except (ValueError, ImportError):
    Modulemd = None

if six.PY2:
    ConfigParser = configparser.SafeConfigParser
else:
    # The SafeConfigParser class has been renamed to ConfigParser in Python 3.2.
    ConfigParser = configparser.ConfigParser

try:
    from rpmautospec import specfile_uses_rpmautospec
except ImportError:
    specfile_uses_rpmautospec = None

try:
    from rpmautospec import \
        calculate_release_number as rpmautospec_calculate_release_number
    from rpmautospec import process_distgit as rpmautospec_process_distgit
except ImportError:
    rpmautospec_process_distgit = None
    rpmautospec_calculate_release_number = None


class NullHandler(logging.Handler):
    """Null logger to avoid spurious messages, add a handler in app code"""
    def emit(self, record):
        pass


h = NullHandler()
# This is our log object, clients of this library can use this object to
# define their own logging needs
log = logging.getLogger(__name__)
# Add the null handler
log.addHandler(h)


class Commands(object):
    """This is a class to hold all the commands that will be called
    by clients
    """

    def __init__(self, path, lookaside, lookasidehash, lookaside_cgi,
                 gitbaseurl, anongiturl, branchre, kojiprofile,
                 build_client, user=None,
                 dist=None, target=None, quiet=False,
                 distgit_namespaced=False, realms=None, lookaside_namespaced=False,
                 git_excludes=None, results_dir='root'):
        """Init the object and some configuration details."""

        # Path to operate on, most often pwd
        self._path = None
        self.path = os.path.abspath(path)
        # The url of the lookaside for source archives
        self.lookaside = lookaside
        # The type of hash to use with the lookaside
        self.lookasidehash = lookasidehash
        # The CGI server for the lookaside
        self.lookaside_cgi = lookaside_cgi
        # Additional arguments needed for lookaside url expansion
        self.lookaside_request_params = None
        # The base URL of the git server
        self.gitbaseurl = gitbaseurl
        # The anonymous version of the git url
        self.anongiturl = anongiturl
        # The regex of branches we care about
        self.branchre = branchre
        # The location of the buildsys config file
        self.kojiprofile = kojiprofile
        # Koji profile of buildsys to build packages
        # The buildsys client to use
        self.build_client = build_client
        # A way to override the discovered "distribution"
        self.dist = dist
        # Set the default hashtype
        self.hashtype = 'sha256'
        # Set an attribute for quiet or not
        self.quiet = quiet
        # Set place holders for properties
        # Anonymous buildsys session
        self._anon_kojisession = None
        # The upstream branch a downstream branch is tracking
        self._branch_merge = None
        # The latest commit
        self._commit = None
        # The disttag rpm value
        self._disttag = None
        # The distval rpm value
        self._distval = None
        # The distvar rpm value
        self._distvar = None
        # The rpm epoch of the cloned package
        self._epoch = None
        # An authenticated buildsys session
        self._kojisession = None
        # A web url of the buildsys server
        self._kojiweburl = None
        # The local arch to use in rpm building
        self._localarch = None
        # A property to load the mock config
        self._mockconfig = None
        # The dist git namespace
        self._ns = None
        # The package name from spec file
        self._package_name_spec = None
        # The rpm name-version-release of the cloned package
        self._nvr = None
        # The rpm release of the cloned package
        self._rel = None
        # Whether the spec file uses %autorelease
        self._uses_autorelease = None
        # Whether the spec file uses rpmautospec features (at all)
        self._uses_rpmautospec = None
        # The cloned repo object
        self._repo = None
        # The rpm defines used when calling rpm
        self._rpmdefines = None
        # The specfile in the cloned package
        self._spec = None
        # The build target within the buildsystem
        self._target = target
        # The build target for containers within the buildsystem
        self._container_build_target = target
        # The build target for flatpaks within the buildsystem
        self._flatpak_build_target = target
        # The top url to our build server
        self._topurl = None
        # The user to use or discover
        self._user = user
        # The password to use
        self._password = None
        # The alternate Koji user to run commands as
        self._runas = None
        # The rpm version of the cloned package
        self._ver = None
        self.log = log
        # Pushurl or url of remote of branch
        self._push_url = None
        # Name of remote determined from current clone
        self._branch_remote = None
        # Name of default remote to be used for new clone
        self.default_branch_remote = 'origin'
        # Default sources file output format type
        self.source_entry_type = 'old'
        # Set an attribute debug
        self.debug = False
        # Set an attribute verbose
        self.verbose = False
        # Configs to set after cloning (namespaces have its own config)
        # These are initialized when detected in config, examples:
        # self.clone_config_rpms = ...
        # self.clone_config_modules = ...
        # self.clone_config_container = ...
        # Git namespacing for more than just rpm build artifacts
        self.distgit_namespaced = distgit_namespaced
        # Kerberos realms used for username detection
        self.realms = realms
        # Whether lookaside cache is namespaced as well. If set to true,
        # package name will be sent to lookaside CGI script as 'namespace/name'
        # instead of just name.
        self.lookaside_namespaced = lookaside_namespaced
        # Deprecates self.module_name
        self._repo_name = None
        # API URL for the module build server
        self.module_api_url = None
        # Namespaces for which retirement is blocked by default.
        self.block_retire_ns = ['rpms']
        # Git excludes patterns
        self.git_excludes = git_excludes or []
        # Results directory type
        self.results_dir = results_dir
        # Layout setup
        self.layout = layout.build(self.path,
                                   'resultsdir' if self.results_dir == 'subdir' else None)

    # Define properties here
    # Properties allow us to "lazy load" various attributes, which also means
    # that we can do clone actions without knowing things like the spec
    # file or rpm data.

    @cached_property
    def lookasidecache(self):
        """A helper to interact with the lookaside cache

        Downstream users of the pyrpkg API may override this property with
        their own, returning their own implementation of a lookaside cache
        helper object.

        :return: lookaside cache instance providing all the needed stuff to
            communicate with a Fedora-style lookaside cache.
        :rtype: :py:class:`pyrpkg.lookaside.CGILookasideCache`
        """
        return CGILookasideCache(
            self.lookasidehash, self.lookaside, self.lookaside_cgi,
            client_cert=self.cert_file, ca_cert=self.ca_cert)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if self._path != value:
            # Ensure all properties which depend on self.path will be
            # freshly loaded next time
            self._push_url = None
            self._branch_remote = None
            self._repo = None
            self._ns = None
        self._path = value

    @property
    def kojisession(self):
        """This property ensures the kojisession attribute"""

        if not self._kojisession:
            self.load_kojisession()
        return self._kojisession

    @property
    def anon_kojisession(self):
        """This property ensures the anon kojisession attribute"""

        if not self._anon_kojisession:
            self.load_kojisession(anon=True)
        return self._anon_kojisession

    def login_koji_session(self, koji_config, session):
        """Login Koji session"""

        authtype = koji_config['authtype']

        # Default to ssl if not otherwise specified and we have the cert
        if authtype == 'ssl' or os.path.isfile(koji_config['cert']) and authtype is None:
            try:
                session.ssl_login(koji_config['cert'],
                                  None,
                                  koji_config['serverca'],
                                  proxyuser=self.runas)
            except Exception as e:
                if koji.is_requests_cert_error(e):
                    self.log.info("Certificate is revoked or expired.")
                raise rpkgAuthError('Could not auth with koji. Login failed: %s' % e)

        # Or try password auth
        elif authtype == 'password' or self.password and authtype is None:
            if self.runas:
                raise rpkgError('--runas cannot be used with password auth')
            session.opts['user'] = self.user
            session.opts['password'] = self.password
            session.login()

        # Or try kerberos
        elif authtype == 'kerberos' or self._has_krb_creds() and authtype is None:
            self.log.debug('Logging into {0} with Kerberos authentication.'.format(
                koji_config['server']))

            if self._load_krb_user():
                try:
                    session.gssapi_login(proxyuser=self.runas)
                except Exception as e:
                    self.log.error('Kerberos authentication fails: %s', e)
            else:
                self.log.warning('Kerberos authentication is used, but you do not have a '
                                 'valid credential.')
                self.log.warning('Please use kinit to get credential with a principal that has '
                                 'realm {0}'.format(', '.join(list(self.realms))))

        if not session.logged_in:
            raise rpkgError('Could not login to %s' % koji_config['server'])

    def load_kojisession(self, anon=False):
        """Initiate a koji session.

        The koji session can be logged in or anonymous
        """
        # Read Koji config from Koji profile
        koji_config = koji.read_config(self.kojiprofile)

        # save the weburl and topurl for later use as well
        self._kojiweburl = koji_config['weburl']
        self._topurl = koji_config['topurl']

        self.log.debug('Initiating a %s session to %s',
                       os.path.basename(self.build_client), koji_config['server'])

        # Build session options used to create instance of ClientSession
        session_opts = koji.grab_session_options(koji_config)

        try:
            session = koji.ClientSession(koji_config['server'], session_opts)
        except Exception:
            raise rpkgError('Could not initiate %s session' % os.path.basename(self.build_client))
        else:
            if anon:
                self._anon_kojisession = session
            else:
                self._kojisession = session

        if not anon:
            self.login_koji_session(koji_config, self._kojisession)

    @property
    def branch_merge(self):
        """This property ensures the branch attribute"""

        if not self._branch_merge:
            self.load_branch_merge()
        return(self._branch_merge)

    @branch_merge.setter
    def branch_merge(self, value):
        self._branch_merge = value

    def load_branch_merge(self):
        """Find the remote tracking branch from the branch we're on.

        The goal of this function is to catch if we are on a branch we can make
        some assumptions about. If there is no merge point then we raise and
        ask the user to specify.
        """

        if self.dist:
            self._branch_merge = self.dist
        else:
            try:
                localbranch = self.repo.active_branch.name
            except TypeError as e:
                raise rpkgError('Repo in inconsistent state: %s' % e)
            try:
                merge = self.repo.git.config('--get', 'branch.%s.merge' % localbranch)
            except git.GitCommandError:
                msg = (
                    'Unable to find remote branch. Use --release\n'
                    'If current branch has to track a remote branch, fix it with command:\n'
                    '    git branch -u origin/%s' % localbranch
                )
                raise rpkgError(msg)
            # Trim off the refs/heads so that we're just working with
            # the branch name
            merge = merge.replace('refs/heads/', '', 1)
            self._branch_merge = merge

    @property
    def branch_remote(self):
        """This property ensures the branch_remote attribute"""

        if not self._branch_remote:
            self.load_branch_remote()
        return self._branch_remote

    def load_branch_remote(self):
        """Find the name of remote from branch we're on."""

        try:
            remote = self.repo.git.config('--get', 'branch.%s.remote'
                                          % self.branch_merge)
        except (git.GitCommandError, rpkgError) as e:
            remote = self.default_branch_remote
            self.log.debug("Could not determine the remote name: %s", str(e))
            self.log.debug("Falling back to default remote name '%s'", remote)

        self._branch_remote = remote

    @property
    def push_url(self):
        """This property ensures the push_url attribute"""

        if not self._push_url:
            self.load_push_url()
        return self._push_url

    def load_push_url(self):
        """Find the pushurl or url of remote of branch we're on."""
        try:
            url = self.repo.git.remote('get-url', '--push', self.branch_remote)
        except git.GitCommandError:
            try:
                url = self.repo.git.config(
                    '--get', 'remote.%s.pushurl' % self.branch_remote)
            except git.GitCommandError:
                try:
                    url = self.repo.git.config(
                        '--get', 'remote.%s.url' % self.branch_remote)
                except git.GitCommandError as e:
                    raise rpkgError('Unable to find remote push url: %s' % e)
        if isinstance(url, six.text_type):
            # GitPython >= 1.0 return unicode. It must be encoded to string.
            self._push_url = url
        else:
            self._push_url = url.decode('utf-8')

    @property
    def commithash(self):
        """This property ensures the commit attribute"""

        if not self._commit:
            self.load_commit()
        return self._commit

    def load_commit(self):
        """Discover the latest commit to the package"""

        # Get the commit hash
        comobj = six.next(self.repo.iter_commits())
        # Work around different versions of GitPython
        if hasattr(comobj, 'sha'):
            self._commit = comobj.sha
        else:
            self._commit = comobj.hexsha

    @property
    def disttag(self):
        """This property ensures the disttag attribute"""

        if not self._disttag:
            self.load_rpmdefines()
        return self._disttag

    @property
    def distval(self):
        """This property ensures the distval attribute"""

        if not self._distval:
            self.load_rpmdefines()
        return self._distval

    @property
    def distvar(self):
        """This property ensures the distvar attribute"""

        if not self._distvar:
            self.load_rpmdefines()
        return self._distvar

    @property
    def epoch(self):
        """This property ensures the epoch attribute"""

        if not self._epoch:
            self.load_nameverrel()
        return self._epoch

    @property
    def kojiweburl(self):
        """This property ensures the kojiweburl attribute"""

        if not self._kojiweburl:
            self.load_kojisession()
        return self._kojiweburl

    @property
    def localarch(self):
        """This property ensures the localarch attribute"""

        if not self._localarch:
            self.load_localarch()
        return(self._localarch)

    def load_localarch(self):
        """Get the local arch as defined by rpm"""

        proc = subprocess.Popen(['rpm --eval %{_arch}'], shell=True,
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
        self._localarch = proc.communicate()[0].strip('\n')

    @property
    def mockconfig(self):
        """This property ensures the mockconfig attribute"""

        if not self._mockconfig:
            self.load_mockconfig()
        return self._mockconfig

    @mockconfig.setter
    def mockconfig(self, config):
        self._mockconfig = config

    def load_mockconfig(self):
        """This sets the mockconfig attribute"""

        self._mockconfig = '%s-%s' % (self.target, self.localarch)

    @property
    def repo_name(self):
        """Property to get repository name

        .. versionadded:: 1.55
        """
        if not self._repo_name:
            self.load_repo_name()
        return self._repo_name

    @repo_name.setter
    def repo_name(self, name):
        """Set repository name"""
        self._repo_name = name

    def load_repo_name(self):
        """Loads repository name

        .. versionadded:: 1.55
        """

        try:
            if self.push_url:
                parts = urllib.parse.urlparse(self.push_url)

                # FIXME
                # if self.distgit_namespaced:
                #     self._module_name = "/".join(parts.path.split("/")[-2:])
                repo_name = posixpath.basename(parts.path.strip('/'))

                if repo_name.endswith('.git'):
                    repo_name = repo_name[:-len('.git')]
                self._repo_name = repo_name
                return
        except rpkgError:
            self.log.warning('Failed to get repository name from Git url or pushurl')

        self.load_nameverrel()
        if self._package_name_spec:
            self._repo_name = self._package_name_spec
            return

        raise rpkgError('Could not find current repository name.'
                        ' Use --name and optional --namespace.')

    @property
    def ns(self):
        """This property provides the namespace of the repository"""

        if not self._ns:
            self.load_ns()
        return self._ns

    @ns.setter
    def ns(self, ns):
        self._ns = ns

    def load_ns(self):
        """Loads the namespace"""

        try:
            if self.distgit_namespaced:
                if self.push_url:
                    parts = urllib.parse.urlparse(self.push_url)

                    path_parts = [p for p in parts.path.split("/") if p]
                    if len(path_parts) == 1:
                        path_parts.insert(0, "rpms")
                    ns = path_parts[-2]

                    self._ns = ns
            else:
                self._ns = None
                self.log.info("Could not find ns, distgit is not namespaced")
        except rpkgError:
            self.log.warning('Failed to get ns from Git url or pushurl')

    @property
    def ns_repo_name(self):
        """Return repository name with namespace

        .. versionadded:: 1.55
        """
        if self.distgit_namespaced:
            return '%s/%s' % (self.ns, self.repo_name)
        else:
            return self.repo_name

    @property
    def nvr(self):
        """This property ensures the nvr attribute"""

        if not self._nvr:
            self.load_nvr()
        return self._nvr

    def load_nvr(self):
        """This sets the nvr attribute"""

        self._nvr = '%s-%s-%s' % (self.repo_name, self.ver, self.rel)

    @property
    def rel(self):
        """This property ensures the rel attribute"""
        if self._rel is None:
            self.load_nameverrel()
        return(self._rel)

    @property
    def uses_autorelease(self):
        if self._uses_autorelease is None:
            self.load_nameverrel()
        return self._uses_autorelease

    @property
    def uses_rpmautospec(self):
        if self._uses_rpmautospec is None:
            self.load_nameverrel()
        return self._uses_rpmautospec

    def load_nameverrel(self):
        """Set the release of a package."""

        #  If the repo is a container, we check for 'verrel' information in the Dockerfile.
        if self.ns in ("container", "containers"):
            if os.path.isfile(os.path.join(self.layout.root_dir, "Dockerfile")):
                docker_name, docker_version, docker_release = self.load_nameverrel_dockerfile()

                self._package_name_spec = docker_name
                self._epoch = "0"
                self._ver = docker_version
                self._rel = docker_release
                return
            else:
                raise rpkgError("Dockerfile for {0} not found.".format(self.repo_name))

        #  Otherwise, we get 'verrel' information from the '.spec' file.
        cmd = ['rpm']
        cmd.extend(self.rpmdefines)

        specfile_path = os.path.join(self.layout.specdir, self.spec)

        if specfile_uses_rpmautospec:
            self._uses_autorelease = specfile_uses_rpmautospec(
                specfile_path, check_autorelease=True, check_autochangelog=False
            )
            self._uses_rpmautospec = specfile_uses_rpmautospec(specfile_path)
            if self._uses_rpmautospec and rpmautospec_calculate_release_number:
                release_number = rpmautospec_calculate_release_number(specfile_path)
                cmd.append("--define '_rpmautospec_release_number %d'" % release_number)
        else:
            # Set to 0 so it evaluates false-ish but differs from (unset) None.
            self._uses_autorelease = 0
            self._uses_rpmautospec = 0

        # We make sure there is a space at the end of our query so that
        # we can split it later.  When there are subpackages, we get a
        # listing for each subpackage.  We only care about the first.
        cmd.extend(['-q', '--qf', '"??%{NAME} %{EPOCH} %{VERSION} %{RELEASE}??"',
                    '--specfile', '"%s"' % specfile_path])
        joined_cmd = ' '.join(cmd)
        try:
            proc = subprocess.Popen(joined_cmd, shell=True,
                                    universal_newlines=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            output, err = proc.communicate()
        except Exception as e:
            self.log.debug('Errors occoured while running following command to get N-V-R-E:')
            self.log.debug(joined_cmd)
            raise rpkgError('Could not query n-v-r of %s: %s'
                            % (self.repo_name, e))
        if err:
            self.log.debug('Errors occoured while running following command to get N-V-R-E:')
            self.log.debug(joined_cmd)
            self.log.error(err)
        if proc.returncode > 0:
            raise rpkgError('Could not get n-v-r-e from %s'
                            % os.path.join(self.layout.specdir, self.spec))

        # Get just the output, then split it by ??, grab the first and split
        # again to get ver and rel
        first_line_output = output.split('??')[1]
        parts = first_line_output.split()
        if len(parts) != 4:
            raise rpkgError('Could not get n-v-r-e from %r'
                            % first_line_output)
        (self._package_name_spec,
         self._epoch,
         self._ver,
         self._rel) = parts

        # Most packages don't include a "Epoch: 0" line, in which case RPM
        # returns '(none)'
        if self._epoch == "(none)":
            self._epoch = "0"

    @property
    def repo(self):
        """This property ensures the repo attribute"""

        if not self._repo:
            self.load_repo()
        return(self._repo)

    def load_repo(self):
        """Create a repo object from our path"""

        self.log.debug('Creating repo object from %s', self.path)
        try:
            self._repo = git.Repo(self.path)
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            raise rpkgError('%s is not a valid repo' % self.path)

    @property
    def rpmdefines(self):
        """This property ensures the rpm defines"""

        if not self._rpmdefines:
            self.load_rpmdefines()
        return(self._rpmdefines)

    def load_rpmdefines(self):
        """Populate rpmdefines based on current active branch"""

        # This is another function ripe for subclassing

        try:
            # This regex should find the 'rhel-5' or 'rhel-6.2' parts of the
            # branch name.  There should only be one of those, and all branches
            # should end in one.
            osver = re.search(r'rhel-\d.*$', self.branch_merge).group()
        except AttributeError:
            raise rpkgError('Could not find the base OS ver from branch name'
                            ' %s. Consider using --release option' %
                            self.branch_merge)
        if self.layout is None:
            raise rpkgError('Unexpected error while loading the package.')
        self._distvar, self._distval = osver.split('-')
        self._distval = self._distval.replace('.', '_')
        self._disttag = 'el%s' % self._distval
        self._rpmdefines = ["--define '_sourcedir %s'" % self.layout.sourcedir,
                            "--define '_specdir %s'" % self.layout.specdir,
                            "--define '_builddir %s'" % self.layout.builddir,
                            "--define '_srcrpmdir %s'" % self.layout.srcrpmdir,
                            "--define '_rpmdir %s'" % self.layout.rpmdir,
                            "--define '_rpmfilename %s'" % self.layout.rpmfilename,
                            "--define 'dist .%s'" % self._disttag,
                            "--define '%s %s'" % (self._distvar,
                                                  self._distval.split('_')[0]),
                            # int and float this to remove the decimal
                            "--define '%s 1'" % self._disttag]

    @property
    def spec(self):
        """This property ensures the spec attribute"""

        if not self._spec:
            self.load_spec()
        return self._spec

    def load_spec(self):
        """This sets the spec attribute"""

        if self.layout is None:
            raise rpkgError('Spec file is not available')

        if self.is_retired():
            raise rpkgError('This package or module is retired. The action has stopped.')

        # Get a list of files in the path we're looking at
        files = os.listdir(self.layout.specdir)
        # Search the files for the first one that ends with ".spec"
        for f in files:
            if f.endswith('.spec') and not f.startswith('.'):
                self._spec = f
                return
        raise rpkgError('No spec file found.')

    @property
    def target(self):
        """This property ensures the target attribute"""

        if not self._target:
            self.load_target()
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    def load_target(self):
        """This creates the target attribute based on branch merge"""

        # If a site has a different naming scheme, this would be where
        # a site would override
        self._target = self.build_target(self.branch_merge)

    def build_target(self, release):
        """Construct build target

        A build target is generally constructed by release and suffix
        ``-candidate``.

        :param str release: the release name which is part of the target name.
        """
        return '{0}-candidate'.format(release)

    @property
    def container_build_target(self):
        """This property ensures the target for container builds."""
        if not self._container_build_target:
            self.load_container_build_target()
        return self._container_build_target

    def load_container_build_target(self):
        """This creates a target based on git branch and namespace."""
        self._container_build_target = '%s-%s-candidate' % (self.branch_merge, self.ns)

    @property
    def flatpak_build_target(self):
        """This property ensures the target for flatpak builds."""
        if not self._flatpak_build_target:
            self.load_flatpak_build_target()
        return self._flatpak_build_target

    def _find_platform_stream(self, name, stream, version=None):
        """Recursively search for the platform module in dependencies to find its stream.

        The stream of the 'platform' pseudo-module determines what base package set
        we need for the runtime - and thus what build target we need.
        """
        if Modulemd is None:
            raise rpkgError("libmodulemd is required by this feature. "
                            "Is not installed or not available for this platform.")

        if version is not None:
            nsvc = name + ':' + stream + ':' + version
        else:
            nsvc = name + ':' + stream

        build = self.module_get_latest_build(nsvc)

        if build is None:
            raise rpkgError("Cannot find any builds for module %s" % nsvc)

        mmd_str = build['modulemd']

        try:
            module_stream = Modulemd.ModuleStream.read_string(mmd_str, strict=False)
        except Exception:
            raise rpkgError("Failed to load modulemd for %s" % nsvc)
        module_stream.upgrade(2)

        # Streams should already be expanded in the modulemd's that we retrieve
        # from MBS - modules were built against a particular dependency.
        def get_stream(dep, req):
            req_stream_list = dep.get_runtime_streams(req)
            if len(req_stream_list) != 1:
                raise rpkgError("%s: stream list for '%s' is not expanded (%s)" %
                                (nsvc, req, req_stream_list))
            return req_stream_list[0]

        # We first look for 'platform' as a direct dependency of this module,
        # before recursing into the dependencies
        for dep in module_stream.get_dependencies():
            for req in dep.get_runtime_modules():
                if req == 'platform':
                    return get_stream(dep, req)

        # Now recurse into the dependencies
        for dep in module_stream.get_dependencies():
            for req in dep.get_runtime_modules():
                platform_stream = self._find_platform_stream(
                    req, get_stream(dep, req)
                )
                if platform_stream:
                    return platform_stream

        return None

    def load_flatpak_build_target(self):
        """This locates a target appropriate for the runtime that the Flatpak targets."""

        # Find the module we are going to build from container.yaml
        yaml_path = os.path.join(self.path, "container.yaml")
        if not os.path.exists(yaml_path):
            raise rpkgError("Cannot find 'container.yaml' to determine build target.")

        with open(yaml_path) as f:
            container_yaml = yaml.safe_load(f)

        compose = container_yaml.get('compose', {})
        modules = compose.get('modules', [])
        if not modules:
            raise rpkgError("No modules listed in 'container.yaml'")
        if len(modules) > 1:
            raise rpkgError("Multiple modules listed in 'container.yaml'")
        module = modules[0]

        # The module can include a profile to specify what packages to
        # put in the Flatpak container Strip it out, since we don't
        # need it for finding the platform stream
        if '/' in module:
            module, _ = module.rsplit('/', 1)

        parts = module.split(':')
        if len(parts) == 2:
            name, stream = parts
            version = None
        elif len(parts) == 3:
            name, stream, version = parts
        else:
            raise rpkgError("Module in container.yaml should be NAME:STREAM[:VERSION][/PROFILE]")

        platform_stream = self._find_platform_stream(name, stream, version=version)
        if platform_stream is None:
            raise rpkgError("Unable to find 'platform' module in the dependencies of '%s'; "
                            "can't determine target" % module)

        self._flatpak_build_target = '%s-flatpak-candidate' % platform_stream

    @property
    def topurl(self):
        """This property ensures the topurl attribute"""

        if not self._topurl:
            # Assume anon here, whatever.
            self.load_kojisession(anon=True)
        return self._topurl

    @property
    def user(self):
        """This property ensures the user attribute"""

        if not self._user:
            self._user = self._load_krb_user()
            if not self._user:
                self.load_user()
        return self._user

    def _load_krb_user(self):
        """This attempts to get the username from active tickets"""

        if not self.realms:
            return None

        if not isinstance(self.realms, list):
            self.realms = [self.realms]

        for realm in self.realms:
            username = cccolutils.get_user_for_realm(realm)
            if username:
                return username
        # We could not find a username for any of the realms, let's fall back
        return None

    def load_user(self):
        """This sets the user attribute"""

        # If a site figures out the user differently (like from ssl cert)
        # this is where you'd override and make that happen
        self._user = getpass.getuser()

    @property
    def password(self):
        """This property ensures the password attribute"""

        return self._password

    @password.setter
    def password(self, password):
        self._password = password

    @property
    def runas(self):
        """This property ensures the runas attribute"""

        return self._runas

    @runas.setter
    def runas(self, runas):
        self._runas = runas

    @property
    def ver(self):
        """This property ensures the ver attribute"""
        if not self._ver:
            self.load_nameverrel()
        return(self._ver)

    @property
    def mock_results_dir(self):
        return os.path.join(self.path, "results_%s" % self.repo_name,
                            self.ver, self.rel)

    @property
    def sources_filename(self):
        if self.layout is None:
            return os.path.join(self.path, 'sources')
        return os.path.join(self.path, self.layout.sources_file_template)

    @property
    def osbs_config_filename(self):
        return os.path.join(self.path, '.osbs-repo-config')

    @property
    def cert_file(self):
        """A client-side certificate for SSL authentication

        Downstream users of the pyrpkg API should override this property if
        they actually need to use a client-side certificate.

        This defaults to None, which means no client-side certificate is used.
        """
        return None

    @property
    def ca_cert(self):
        """A CA certificate to authenticate the server in SSL connections

        Downstream users of the pyrpkg API should override this property if
        they actually need to use a CA certificate, usually because their
        lookaside cache is using HTTPS with a self-signed certificate.

        This defaults to None, which means the system CA bundle is used.
        """
        return None

    # Define some helper functions, they start with _

    def _has_krb_creds(self):
        """
        Kerberos authentication is disabled if neither gssapi nor krbV is
        available
        """
        return cccolutils.has_creds()

    def _run_command(self, cmd, shell=False, env=None, pipe=[], cwd=None,
                     return_stdout=False, return_stderr=False,
                     return_text=False):
        """Run the given command.

        `_run_command` is able to run single command or two commands via pipe.
        Whatever the way to run the command, output to both stdout and stderr
        will not be captured and output to terminal directly, that is useful
        for caller to redirect.

        :param cmd: executable and arguments to run. Depending on argument
            `shell`, `cmd` could be a list if `shell` is `False`, and a string
            if `False` is passed to `shell`.
        :type cmd: str or list
        :param bool shell: whether to run in a shell or not, defaults to
            `False`.
        :param env: environment variables to use (if any)
        :type env: dict(str, str)
        :param pipe: command to pipe the output of `cmd` into. Same as argument
            `cmd`, `pipe` could be a string or list depending on value of
            `shell`.
        :type pipe: str or list
        :param str cwd: optional directory to run the command from
        :param bool return_stdout: whether to capture output to stdout and
            return it. Default is False.
        :param bool return_stderr: whether to capture output to stderr and
            return it. Default is False.
        :param bool return_text: whether to return the stdout and stder output
            as text instead of byte string. Default is False.
        :return: a tuple containing three values of exit code from process,
            output to stdout, output to stderr. Either output to stdout or
            stderr could be None if `return_stdout` or `return_stderr` is not
            set.
        :rtype: tuple(int, str, str)
        :raises rpkgError: any error raised from underlying
            `subprocess` while executing command in local system will be mapped
            to :py:exc:`rpkgError`. In addition, if process returns non-zero
            and error message output to stderr does not intent to be returned,
            the error is raised as well.

        .. versionchanged:: 1.56
           Added argument return_stdout, return_stderr and return_text.
           Return process exit code, output to stdout and stderr if process
           executes successfully.
        """

        # Process any environment variables.
        environ = os.environ
        if env:
            for item in env.keys():
                self.log.debug('Adding %s:%s to the environment', item, env[item])
                environ[item] = env[item]
        # Check if we're supposed to be on a shell.  If so, the command must
        # be a string, and not a list.
        command = cmd
        pipecmd = pipe
        if shell:
            command = ' '.join(cmd)
            pipecmd = ' '.join(pipe)

        if pipe:
            self.log.debug('Running: %s | %s', ' '.join(cmd), ' '.join(pipe))
        else:
            self.log.debug('Running: %s', ' '.join(cmd))

        proc_stdout = subprocess.PIPE if return_stdout else None
        proc_stderr = subprocess.PIPE if return_stderr else None

        try:
            if pipe:
                # We're piping the stderr over as well, which is probably a
                # bad thing, but rpmbuild likes to put useful data on
                # stderr, so....
                parent_proc = subprocess.Popen(
                    command, env=environ, shell=shell, cwd=cwd,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                proc = subprocess.Popen(
                    pipecmd, env=environ, shell=shell, cwd=cwd,
                    stdin=parent_proc.stdout,
                    stdout=proc_stdout, stderr=proc_stderr,
                    universal_newlines=return_text)
            else:
                proc = subprocess.Popen(
                    command, env=environ, shell=shell, cwd=cwd,
                    stdout=proc_stdout, stderr=proc_stderr,
                    universal_newlines=return_text)
        except KeyboardInterrupt:
            raise rpkgError('Command is terminated by user.')
        except Exception as e:
            raise rpkgError(e)

        exit_code = proc.wait()
        if exit_code > 0 and not return_stderr:
            raise rpkgError('Failed to execute command.')

        return (
            exit_code,
            proc.stdout.read() if return_stdout else None,
            proc.stderr.read() if return_stderr else None,
        )

    def _newer(self, file1, file2):
        """Compare the last modification time of the given files

        :return: True if file1 is newer than file2
        :rtype: bool
        """

        return os.path.getmtime(file1) > os.path.getmtime(file2)

    def _get_build_arches_from_spec(self):
        """Given the path to an spec, retrieve the build arches"""

        spec = os.path.join(self.path, self.spec)
        try:
            hdr = rpm.spec(spec)
        except Exception:
            raise rpkgError('%s is not a spec file' % spec)
        archlist = [pkg.header['arch'] for pkg in hdr.packages]
        if not archlist:
            raise rpkgError('No compatible build arches found in %s' % spec)
        if six.PY3:
            return [str(arch, encoding='utf-8')
                    if not isinstance(arch, six.string_types)
                    else arch
                    for arch in archlist]
        else:
            return archlist

    def _get_build_arches_from_srpm(self, srpm, arches):
        """Given the path to an srpm, determine the possible build arches

        Use supplied arches as a filter, only return compatible arches
        """

        archlist = arches
        hdr = koji.get_rpm_header(srpm)
        if hdr[rpm.RPMTAG_SOURCEPACKAGE] != 1:
            raise rpkgError('%s is not a source package.' % srpm)
        buildarchs = hdr[rpm.RPMTAG_BUILDARCHS]
        exclusivearch = hdr[rpm.RPMTAG_EXCLUSIVEARCH]
        excludearch = hdr[rpm.RPMTAG_EXCLUDEARCH]
        # Reduce by buildarchs
        if buildarchs:
            archlist = [a for a in archlist if a in buildarchs]
        # Reduce by exclusive arches
        if exclusivearch:
            archlist = [a for a in archlist if a in exclusivearch]
        # Reduce by exclude arch
        if excludearch:
            archlist = [a for a in archlist if a not in excludearch]
        # do the noarch thing
        if 'noarch' not in excludearch and ('noarch' in buildarchs or
                                            'noarch' in exclusivearch):
            archlist.append('noarch')
        # See if we have anything compatible.  Should we raise here?
        if not archlist:
            raise rpkgError('No compatible build arches found in %s' % srpm)
        return archlist

    def _guess_hashtype(self):
        """Attempt to figure out the hash type based on branch data"""

        # We may not be able to determine the rpmdefine, if so, fall back.
        try:
            # This works, except for the small range of Fedoras
            # between FC5 and FC12 or so.  Nobody builds for that old
            # anyway.
            if int(re.search(r'\d+', self.distval).group()) < 6:
                return('md5')
        except Exception:
            # An error here is OK, don't bother the user.
            pass

        # Fall back to the default hash type
        return(self.hashtype)

    def _fetch_remotes(self):
        self.log.debug('Fetching remotes')
        for remote in self.repo.remotes:
            self.repo.git.fetch(remote)

    def _list_branches(self, fetch=True):
        """Returns a tuple of local and remote branch names

        :return: a pair of local branch names and remote branch names.
        :rtype: tuple(list, list)
        """

        if fetch:
            self._fetch_remotes()
        self.log.debug('Listing refs')
        refs = self.repo.refs
        # Sort into local and remote branches
        remotes = []
        locals = []
        for ref in refs:
            if type(ref) == git.Head:
                self.log.debug('Found local branch %s', ref.name)
                locals.append(ref.name)
            elif type(ref) == git.RemoteReference:
                if ref.remote_head == 'HEAD':
                    self.log.debug('Skipping remote branch alias HEAD')
                    continue  # Not useful in this context
                self.log.debug('Found remote branch %s', ref.name)
                remotes.append(ref.name)
        return (locals, remotes)

    def _srpmdetails(self, srpm):
        """Return a tuple of package name, package files, and upload files."""

        try:
            hdr = koji.get_rpm_header(srpm)
            name = hdr[rpm.RPMTAG_NAME]
            contents = hdr[rpm.RPMTAG_FILENAMES]
            if six.PY3 and not isinstance(name, six.string_types):
                # RPM before rhbz#1693751 returned bytes
                name = str(name, encoding='utf-8')
                contents = [str(filename, encoding='utf-8')
                            for filename in contents]
        except Exception as e:
            raise rpkgError('Error querying srpm: {0}'.format(str(e)))

        # now get the files and upload files
        files = []
        uploadfiles = []

        # prepare temp directory to extract srpm there
        target_dir = tempfile.mkdtemp(suffix="extract-srpm", prefix="rpkg")
        try:
            try:
                self.log.debug("Extracting srpm '{0}', destination '{1}'".format(
                    srpm, target_dir
                ))
                # method 'is_lookaside_eligible_file' will access extracted
                # files to detect its encoding (binary or not)
                _, _ = extract_srpm(srpm, target_dir)
            except Exception as e:
                self.log.error("Extraction of srpm has failed {0}".format(e))
                raise

            # Cycle through the srpm content and decide where to upload files
            for file in contents:
                if os.path.isdir(os.path.join(target_dir, file)):
                    # only show warning; file-dir will be skipped during
                    # the test of eligibility
                    self.log.warning("SRPM file contains a directory: '{0}'. "
                                     "Skipping it.".format(file))
                if is_lookaside_eligible_file(file, target_dir):
                    uploadfiles.append(file)
                else:
                    files.append(file)
        finally:
            shutil.rmtree(target_dir)

        return (name, files, uploadfiles)

    def _get_namespace_giturl(self, repo_name):
        """Get the namespaced git url, if DistGit namespace enabled

        :param str repo_name: a repository name with or without namespace.
        :return: giturl with proper namespace. If namespace is not in the
            repository name and dist-git namespace is enabled, default
            namespace rpms will set.
        :rtype: str
        """
        if self.distgit_namespaced and '/' not in repo_name:
            # Default to rpms namespace for backwards compat
            repo_name = 'rpms/%s' % repo_name

        giturl = self.gitbaseurl % {
            'user': self.user,
            'repo': repo_name,
            # This is for the compatible with old format
            'module': repo_name
        }
        return giturl

    def _get_namespace_anongiturl(self, repo_name):
        """Get the namespaced git url, if DistGit namespace enabled

        :param str repo_name: a repository name with or without namespace.
        :return: anonymous giturl with a proper namespace. If repository name
            does not have namespace and dist-git namespace is enabled, default
            namespace rpms will be set.
        :rtype: str
        """
        if self.distgit_namespaced and '/' not in repo_name:
            # Default to rpms namespace for backwards compat
            repo_name = 'rpms/%s' % repo_name

        giturl = self.anongiturl % {
            'repo': repo_name,
            # This is for the compatible with old format
            'module': repo_name,
        }
        return giturl

    def add_tag(self, tagname, force=False, message=None, file=None):
        """Add a git tag to the repository

        :param str tagname: tag name.
        :param bool force: Optionally can force the tag, include a message, or
            reference a message file.
        :param str file: Optional. File containing tag message.
        """

        cmd = ['git', 'tag']
        cmd.extend(['-a'])
        # force tag creation, if tag already exists
        if force:
            cmd.extend(['-f'])
        # Description for the tag
        if message:
            cmd.extend(['-m', message])
        elif file:
            cmd.extend(['-F', os.path.abspath(file)])
        cmd.append(tagname)
        # make it so
        self._run_command(cmd, cwd=self.path)
        self.log.info('Tag \'%s\' was created', tagname)

    def clean(self, dry=False, useignore=True):
        """Clean a repository checkout of untracked files.

        :param bool dry: Can optionally perform a dry-run. Defaults to `False`.
        :param bool useignore: Can optionally not use the ignore rules.
            Defaults to `True`.
        """

        # setup the command, this could probably be done with some python api...
        cmd = ['git', 'clean', '-f', '-d']
        if dry:
            cmd.append('--dry-run')
        if not useignore:
            cmd.append('-x')
        if self.quiet:
            cmd.append('-q')
        # Run it!
        self._run_command(cmd, cwd=self.path)
        return

    def clone(self, repo, path=None, branch=None, bare_dir=None,
              anon=False, target=None, depth=None, extra_args=None):
        """Clone a repo, optionally check out a specific branch.

        :param str repo: the name of the repository to clone.
        :param str path: an optional basedir to perform the clone in.
        :param str branch: an optional name of a branch to checkout instead of
            `<remote>/master`.
        :param str bare_dir: an optional name of a directory to make a bare
            clone to if this is a bare clone. `None` otherwise.
        :param bool anon: whether or not to clone anonymously. Defaults to
            `False`.
        :param str target: an optional name of the folder in which to clone the
            repo.
        :param int depth: create a shallow clone with a history truncated
            to the specified number of commits.
        :param list extra_args: additional arguments that are passed to
            the clone command.
        """

        if not path:
            path = self.path
            self._push_url = None
            self._branch_remote = None
        # construct the git url
        if anon:
            giturl = self._get_namespace_anongiturl(repo)
        else:
            giturl = self._get_namespace_giturl(repo)

        # Create the command
        cmd = ['git', 'clone']
        if self.quiet:
            cmd.append('-q')
        if depth:
            cmd.extend(['--depth', depth])
        # do the clone
        if branch and bare_dir:
            raise rpkgError('Cannot combine bare cloning with a branch')
        elif branch:
            # For now we have to use switch branch
            self.log.debug('Checking out a specific branch %s', giturl)
            cmd.extend(['-b', branch, giturl])
        elif bare_dir:
            self.log.debug('Cloning %s bare', giturl)
            cmd.extend(['--bare', giturl])
            if not target:
                cmd.append(bare_dir)
        else:
            self.log.debug('Cloning %s', giturl)
            cmd.extend([giturl])

        if not bare_dir:
            # --bare and --origin are incompatible
            cmd.extend(['--origin', self.default_branch_remote])
        if extra_args:
            cmd.extend(extra_args)
            self.log.debug("Extra args '{0}' are passed to git clone "
                           "command".format(extra_args))
        if target:
            self.log.debug('Cloning into: %s', target)
            cmd.append(target)

        self._run_command(cmd, cwd=path)

        # Set configuration
        base_repo = self.get_base_repo(repo)
        git_dir = target if target else bare_dir if bare_dir else base_repo
        conf_git = git.Git(os.path.join(path, git_dir))
        self._clone_config(conf_git, repo)

        if not bare_dir:
            self._add_git_excludes(os.path.join(path, git_dir))

        return

    def get_base_repo(self, repo):
        # Handle namespaced repositories
        # Example:
        #   repository: docker/cockpit
        #       The path will just be os.path.join(path, "cockpit")
        #   repository: rpms/nodejs
        #       The path will just be os.path.join(path, "nodejs")
        if "/" in repo:
            return repo.split("/")[-1]
        return repo

    def clone_with_dirs(self, repo, anon=False, target=None, depth=None,
                        extra_args=None):
        """Clone a repo old style with subdirs for each branch.

        :param str repo: name of the repository to clone.
        :param bool anon: whether or not to clone anonymously. Defaults to
            `False`.
        :param str target: an optional name of the folder in which to clone the
            repo.
        :param int depth: create a shallow clone with a history truncated
            to the specified number of commits.
        :param list extra_args: additional arguments that are passed to
            the clone command.
        """

        self._push_url = None
        self._branch_remote = None
        # Get the full path of, and git object for, our directory of branches
        top_path = os.path.join(self.path,
                                target or self.get_base_repo(repo))
        top_git = git.Git(top_path)
        repo_path = os.path.join(top_path, 'rpkg.git')

        # construct the git url
        if anon:
            giturl = self._get_namespace_anongiturl(repo)
        else:
            giturl = self._get_namespace_giturl(repo)

        # Create our new top directory
        try:
            os.mkdir(top_path)
        except OSError as e:
            raise rpkgError('Could not create directory for repository %s: %s'
                            % (repo, e))

        # Create a bare clone first. This gives us a good list of branches
        try:
            self.clone(repo, top_path, bare_dir=repo_path, anon=anon, depth=depth,
                       extra_args=extra_args)
        except Exception:
            # Clean out our directory
            shutil.rmtree(top_path)
            raise
        # Get the full path to, and a git object for, our new bare repo
        repo_git = git.Git(repo_path)

        # Get a branch listing
        branches = [x for x in repo_git.branch().split()
                    if x != "*" and re.search(self.branchre, x)]

        for branch in branches:
            try:
                # Make a local clone for our branch
                top_git.clone("--branch", branch,
                              "--origin", self.default_branch_remote,
                              repo_path, branch)

                # Set configuration
                conf_git = git.Git(os.path.join(top_path, branch))
                self._clone_config(conf_git, repo)

                # Set the origin correctly
                branch_path = os.path.join(top_path, branch)
                branch_git = git.Git(branch_path)
                branch_git.config("--replace-all",
                                  "remote.%s.url" % self.default_branch_remote,
                                  giturl)

                # Add excludes
                self._add_git_excludes(branch_path)
            except (git.GitCommandError, OSError) as e:
                raise rpkgError('Could not locally clone %s from %s: %s'
                                % (branch, repo_path, e))

        # We don't need this now. Ignore errors since keeping it does no harm
        shutil.rmtree(repo_path, ignore_errors=True)

    def _clone_config(self, conf_git, repo):
        # Inject ourselves as the git credential helper for https pushing
        conf_git.config('credential.helper', ' '.join(find_me() + ['gitcred']))
        conf_git.config('credential.useHttpPath', 'true')

        # skip repositories that are not namespaced
        if not self.distgit_namespaced:
            return

        # use "rpms" as a default namespace if omitted
        namespace = repo.split("/")[0] if "/" in repo else "rpms"
        # Has current namespace its own clone config?
        selected_clone_config = None
        if hasattr(self, "clone_config_{0}".format(namespace)):
            selected_clone_config = getattr(self, "clone_config_{0}".format(namespace))

        # Valid configuration is non-empty string
        if selected_clone_config:
            base_repo = self.get_base_repo(repo)
            selected_clone_config = selected_clone_config.strip() % {
                # base_repo will be just the repository name with namespace
                # stripped.
                'repo': base_repo,
                # repo is the repo argument which is passed in the CLI, which
                # could or cound't have namespace. So, if namespace is
                # included, it is just the ns_repo, otherwise it is same as the
                # base_repo.
                'ns_repo': repo,

                # This is for compatible with old format
                'base_module': base_repo,
                'module': repo
            }
            for confline in selected_clone_config.splitlines():
                if confline:
                    # maxsplit=1 because value in clone_config can contain whitespaces
                    conf_git.config(*confline.split(None, 1))

    def _add_git_excludes(self, conf_dir):
        """
        Add a list of patterns from config into the config file in a git
        repository. This list excludes some files or dirs to be tracked by
        git. This list usually includes files that are automatically generated.
        These changes are valid just for local git repository.
        """
        git_excludes_path = os.path.join(conf_dir, '.git/info/exclude')
        git_excludes = GitIgnore(git_excludes_path)
        for item in self.git_excludes:
            git_excludes.add(item)
        if not os.path.exists(git_excludes_path):
            # prepare ".git/info" directory if is missing
            os.makedirs(os.path.dirname(git_excludes_path))
        git_excludes.write()
        self.log.debug('Git-excludes patterns were added into %s' % git_excludes_path)

    def commit(self, message=None, file=None, files=[], signoff=False):
        """Commit changes to a repository (optionally found at path)

        Requires the caller be a real tty or a message passed.

        :param str message: an optional message to use as the commit message
        :param str file: an optional file to find the commit message within
        :param list files: an optional list to list files to commit.
        :param bool signoff: signoff commit optionally. Defaults to `False`.
        """

        # First lets see if we got a message or we're on a real tty:
        if not sys.stdin.isatty():
            if not message and not file:
                raise rpkgError('Must have a commit message or be on a real tty.')

        # construct the git command
        # We do this via subprocess because the git module is terrible.
        cmd = ['git', 'commit']
        if signoff:
            cmd.append('-s')
        if self.quiet:
            cmd.append('-q')
        if message:
            cmd.extend(['-m', message])
        elif file:
            # If we get a relative file name, prepend our path to it.
            if self.path and not file.startswith('/'):
                cmd.extend(['-F', os.path.abspath(os.path.join(self.path, file))])
            else:
                cmd.extend(['-F', os.path.abspath(file)])
        if not files:
            cmd.append('-a')
        else:
            cmd.extend(files)
        # make it so
        self._run_command(cmd, cwd=self.path)
        return

    def delete_tag(self, tagname):
        """Delete a git tag from the repository found at optional path"""

        try:
            self.repo.delete_tag(tagname)

        except git.GitCommandError as e:
            raise rpkgError(e)

        self.log.info('Tag %s was deleted', tagname)

    def diff(self, cached=False, files=[]):
        """Execute a git diff

        :param bool cached: optionally diff the cached or staged changes.
            Defaults to not.
        :param list files: optional list of files to diff relative to the
            module base directory.
        """

        # Things work better if we're in our repository directory
        oldpath = os.getcwd()
        os.chdir(self.path)
        # build up the command
        cmd = ['git', 'diff']
        if cached:
            cmd.append('--cached')
        if files:
            cmd.extend(files)

        # Run it!
        self._run_command(cmd)
        # popd
        os.chdir(oldpath)
        return

    def get_latest_commit(self, repo, branch):
        """Discover the latest commit has for a given repository and return it"""

        # This is stupid that I have to use subprocess :/
        url = self._get_namespace_anongiturl(repo)
        # This cmd below only works to scratch build rawhide
        # We need something better for epel
        cmd = ['git', 'ls-remote', url, 'refs/heads/%s' % branch]
        try:
            proc = subprocess.Popen(cmd,
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    universal_newlines=True)
            output, error = proc.communicate()
        except OSError as e:
            raise rpkgError(e)
        if error:
            raise rpkgError('Got an error finding %s head for %s: %s'
                            % (branch, repo, error))
        # Return the hash sum
        if not output:
            raise rpkgError('Could not find remote branch %s for %s'
                            % (branch, repo))
        return output.split()[0]

    def gitbuildhash(self, build):
        """Determine the git hash used to produce a particular N-V-R"""

        # Get the build data from the nvr
        self.log.debug('Getting task data from the build system')
        bdata = self.anon_kojisession.getBuild(build)
        if not bdata:
            raise rpkgError('Unknown build: %s' % build)

        # Get the task data out of that build data
        taskinfo = self.anon_kojisession.getTaskInfo(bdata["task_id"], request=True)
        request = taskinfo["request"]
        # request is a list of items
        # For RPM builds, the first item is the task url. second is the build target.
        # For Winbuild tasks the url comes second.
        # See if the build target starts with cvs or git
        hash = None
        buildsource = request[1] if taskinfo["method"] == "winbuild" else request[0]
        if buildsource.startswith('cvs://'):
            # snag everything after the last # mark
            cvstag = buildsource.rsplit('#')[-1]
            # Now read the remote repo to figure out the hash from the tag
            giturl = self._get_namespace_anongiturl(bdata['name'])
            cmd = ['git', 'ls-remote', '--tags', giturl, cvstag]
            self.log.debug('Querying git server for tag info')
            try:
                output = subprocess.check_output(cmd)
                hash = output.split()[0]
            except Exception:
                # don't do anything here, we'll handle not having hash
                # later
                pass
        elif buildsource.startswith('git://') or buildsource.startswith('git+https://'):
            # Match a 40 char block of text on the url line, that'll be
            # our hash
            hash = buildsource.rsplit('#')[-1]
        else:
            # Unknown build source
            raise rpkgError('Unhandled build source %s' % buildsource)
        if not hash:
            raise rpkgError('Could not find hash of build %s' % build)
        return (hash)

    def import_srpm(self, srpm):
        """Import the contents of an srpm into a repo.

        This function will add/remove content to match the srpm,
        upload new files to the lookaside, and stage the changes.

        :param str srpm: file to import contents from.
        :return: a list of files to upload.
        :rtype: list
        """
        # bail if we're dirty
        if self.repo.is_dirty():
            raise rpkgError('There are uncommitted changes in your repo')
        # see if the srpm even exists
        srpm = os.path.abspath(srpm)
        if not os.path.exists(srpm):
            raise rpkgError('File not found.')
        # Get the details of the srpm
        name, files, uploadfiles = self._srpmdetails(srpm)

        # Need a way to make sure the srpm name matches the repo some how.

        # Some repositories are created with an initial commit with some files
        # created and committed. Files listed here are what should be reserved
        # while importing a SRPM.
        # The list also contains files, that are important and should
        # not be removed by import command.
        reserved_ourfiles = ['README.md', 'gating.yaml', 'tests/*', '*.rpmlintrc']

        # Get a list of files we're currently tracking
        ourfiles = self.repo.git.ls_files().split('\n')
        if ourfiles == ['']:
            # Repository doesn't contain any files
            ourfiles = []
        else:
            # Trim out sources and .gitignore
            for file in ('.gitignore', 'sources'):
                try:
                    ourfiles.remove(file)
                except ValueError:
                    pass

        # Things work better if we're in our repository directory
        oldpath = os.getcwd()
        os.chdir(self.path)

        # Look through our files and if it isn't in the new files, remove it.
        for file in ourfiles:
            # matches 'file' to any 'reserved_ourfiles' pattern?
            if any(filter(lambda pattern: fnmatch.fnmatch(file, pattern), reserved_ourfiles)):
                continue
            if file not in files:
                self.log.info("Removing no longer used file: %s", file)
                self.repo.index.remove([file])
                os.remove(file)

        try:
            self.log.debug("Extracting srpm '{0}'".format(srpm))
            output, err = extract_srpm(srpm)
        except Exception as e:
            self.log.error("Extraction of srpm has failed {0}".format(e))
            raise
        if output:
            self.log.debug(output)
        if err:
            os.chdir(oldpath)
            raise rpkgError("Got an error from rpm2cpio: %s" % err)

        # And finally add all the files we know about (and our stock files)
        for file in ('.gitignore', 'sources'):
            if not os.path.exists(file):
                # Create the file
                open(file, 'w').close()
            files.append(file)
        self.repo.index.add(files)
        # Return to the caller and let them take it from there.
        os.chdir(oldpath)
        return [os.path.join(self.path, file) for file in uploadfiles]

    def list_tag(self, tagname='*'):
        """List all tags in the repository which match a given tagname.

        :param str tagname: an optional shell glob to match part of tags (it
            is matched with `fnmatch`). Defaults to '`*`' to list all tags.
        """
        if tagname is None:
            tagname = '*'

        tags = map(lambda t: t.name, self.repo.tags)

        if tagname != '*':
            tags = filter(lambda t: fnmatch.fnmatch(t, tagname), tags)

        for tag in tags:
            print(tag)

    def new(self):
        """Return changes in a repo since the last tag"""

        # Find the latest tag
        try:
            tag = self.repo.git.describe('--tags', '--abbrev=0')
        except git.exc.GitCommandError:
            raise rpkgError('Cannot get changes because there are no tags in this repo.')
        # Now get the diff
        self.log.debug('Diffing from tag %s', tag)
        return self.repo.git.diff('-M', tag)

    def patch(self, suffix, rediff=False):
        """Generate a patch from the expanded source and add it to index

        suffix: Look for files named with this suffix to diff
        rediff: optionally retain any comments in the patch file and rediff

        Will create a patch file named name-version-suffix.patch
        """

        # Create the outfile name based on arguments
        outfile = '%s-%s-%s.patch' % (self.repo_name, self.ver, suffix)

        # If we want to rediff, the patch file has to already exist
        if rediff and not os.path.exists(os.path.join(self.path, outfile)):
            raise rpkgError('Patch file %s not found, unable to rediff' %
                            os.path.join(self.path, outfile))

        # See if there is a source dir to diff in
        if not os.path.isdir(os.path.join(self.path,
                                          '%s-%s' % (self.repo_name,
                                                     self.ver))):
            raise rpkgError('Expanded source dir not found!')

        # Setup the command
        cmd = ['gendiff', '%s-%s' % (self.repo_name, self.ver),
               '.%s' % suffix]

        # Try to run the command and capture the output
        try:
            self.log.debug('Running %s', ' '.join(cmd))
            (output, errors) = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                cwd=self.path).communicate()
        except Exception as e:
            raise rpkgError('Error running gendiff: %s' % e)

        # log any errors
        if errors:
            self.log.error(errors)

        # See if we got anything
        if not output:
            raise rpkgError('gendiff generated an empty patch!')

        # See if we are rediffing and handle the old patch file
        if rediff:
            oldpatch = open(os.path.join(self.path, outfile), 'r').readlines()
            # back up the old file
            self.log.debug('Moving existing patch %s to %s~', outfile, outfile)
            os.rename(os.path.join(self.path, outfile),
                      '%s~' % os.path.join(self.path, outfile))
            # Capture the lines preceding the diff
            newhead = []
            for line in oldpatch:
                if line.startswith('diff'):
                    break
                else:
                    newhead.append(line)

            log.debug('Saved from previous patch: \n%s' % ''.join(newhead))
            # Stuff the new head in front of the existing output
            output = ''.join(newhead) + output

        # Write out the patch
        open(os.path.join(self.path, outfile), 'w').write(output)

        # Add it to the index
        # Again this returns a blank line we want to keep quiet
        self.repo.index.add([outfile])
        log.info('Created %s and added it to the index' % outfile)

    def pull(self, rebase=False, norebase=False):
        """Pull changes from the remote repository

        Optionally rebase current branch on top of remote branch

        Optionally override .git setting to always rebase

        """
        self.check_repo(is_dirty=False, all_pushed=False)

        cmd = ['git', 'pull']
        if self.quiet:
            cmd.append('-q')
        if rebase:
            cmd.append('--rebase')
        if norebase:
            cmd.append('--no-rebase')
        self._run_command(cmd, cwd=self.path)
        return

    def find_untracked_patches(self):
        """Find patches that are not tracked by git and sources both"""
        file_pattern = os.path.join(self.path, '*.patch')
        patches_in_repo = [os.path.basename(filename) for filename
                           in glob.glob(file_pattern)]

        git_tree = self.repo.head.commit.tree
        sources_file = SourcesFile(self.sources_filename,
                                   self.source_entry_type)

        patches_not_tracked = [
            patch for patch in patches_in_repo
            if patch not in git_tree and patch not in sources_file]

        return patches_not_tracked

    def push(self, force=False, extra_config=None):
        """Push changes to the remote repository"""
        self.check_repo(is_dirty=False, all_pushed=False)

        # see if our branch is tracking anything
        try:
            self.load_branch_merge()
        except Exception:
            self.log.warning('Current branch cannot be pushed anywhere!')

        untracked_patches = self.find_untracked_patches()
        if untracked_patches:
            self.log.warning(
                'Patches %s %s not tracked within either git or sources',
                ', '.join(untracked_patches),
                'is' if len(untracked_patches) == 1 else 'are')

        cmd = ['git']
        if extra_config:
            for opt in extra_config:
                cmd += ['-c', '%s=%s' % (opt, extra_config[opt])]
        cmd.append('push')
        if force:
            cmd += ['-f']
        if self.quiet:
            cmd.append('-q')
        self._run_command(cmd, cwd=self.path)

    def sources(self, outdir=None):
        """Download source files"""

        if not os.path.exists(self.sources_filename):
            self.log.info("sources file doesn't exist. Source files download skipped.")
            return

        # Default to putting the files where the repository is
        if not outdir:
            outdir = self.path

        sourcesf = SourcesFile(self.sources_filename, self.source_entry_type)
        specf = SpecFile(os.path.join(self.layout.specdir, self.spec))

        args = dict()
        if self.lookaside_request_params:
            if 'branch' in self.lookaside_request_params.split():
                # The value of branch_merge is dynamic property;  to get it's
                # value you need to be in proper branch or you need to first
                # specify --release (which is pretty annoying).  Since not every
                # dist-git instance out there really needs 'branch' argument to
                # expand lookaside cache urls - make it optional.
                args['branch'] = self.branch_merge

        for entry in sourcesf.entries:
            outfile = os.path.join(outdir, entry.file)
            if is_file_tracked(outfile, outdir):
                raise rpkgError(
                    "Error: Attempting a download '{0}' that would override a git tracked file. "
                    "Either remove the corresponding line from 'sources' file to keep the git "
                    "tracked one or 'git rm' the file to allow the download.".format(outfile))
            if (entry.file not in specf.sources):
                self.log.info("Not downloading unused %s" % entry.file)
                continue
            self.lookasidecache.download(
                self.ns_repo_name if self.lookaside_namespaced else self.repo_name,
                entry.file, entry.hash, outfile,
                hashtype=entry.hashtype, **args)

    def switch_branch(self, branch, fetch=True):
        """Switch the working branch

        Will create a local branch if one doesn't already exist,
        based on <remote>/<branch>

        Logs output and returns nothing.
        """

        # Currently this just grabs the first matching branch name from
        # the first remote it finds.  When multiple remotes are in play
        # this needs to get smarter

        self.check_repo(all_pushed=False)

        # Get our list of branches
        (locals, remotes) = self._list_branches(fetch)

        if branch not in locals:
            # We need to create a branch
            self.log.debug('No local branch found, creating a new one')
            totrack = None
            full_branch = '%s/%s' % (self.branch_remote, branch)
            for remote in remotes:
                if remote == full_branch:
                    totrack = remote
                    break
            else:
                raise rpkgError('Unknown remote branch %s' % full_branch)
            try:
                self.log.info(self.repo.git.checkout('-b', branch, '--track', totrack))
            except Exception as err:
                # This needs to be finer grained I think...
                raise rpkgError('Could not create branch %s: %s'
                                % (branch, err))
        else:
            try:
                self.repo.git.checkout(branch)
                # The above should have no output, but stash it anyway
                self.log.info("Switched to branch '%s'", branch)
            except Exception as err:
                # This needs to be finer grained I think...
                raise rpkgError('Could not check out %s\n%s' % (branch,
                                                                err.stderr))
        return

    def check_repo(self, is_dirty=True, has_namespace=True, all_pushed=True):
        """Check various status of current repository

        :param bool is_dirty: Default to True. To check whether there is uncommitted changes.
        :param bool has_namespace: Default to True. To check whether this repo
            is checked out with namespace, e.g. rpms/, docker/. If the repo is
            an old checkout, warn user with message how to fix it.
        :param bool all_pushed: Default to True. To check whether all changes are pushed.
        :raises rpkgError: if any unexpected status is detected. For example,
            if changes are not committed yet.
        """
        if is_dirty:
            if self.repo.is_dirty():
                raise rpkgError('%s has uncommitted changes.  Use git status '
                                'to see details' % self.path)
        if has_namespace:
            try:
                repo_name = self.push_url
            except rpkgError:
                # Ignore error if cannot get remote push URL from this repo.
                # That is we just skip has_namespace check when that error
                # happens.
                pass
            else:
                parts = urllib.parse.urlparse(repo_name)
                parts = [p for p in parts.path.split('/') if p]
                not_contain_namespace = len(parts) == 1
                if not_contain_namespace:
                    self.log.warning('Your git configuration does not use a namespace.')
                    self.log.warning('Consider updating your git configuration by running:')
                    self.log.warning('  git remote set-url %s %s',
                                     self.branch_remote, self._get_namespace_giturl(parts[0]))
        if all_pushed:
            branch = self.repo.active_branch
            try:
                remote = self.repo.git.config('--get', 'branch.%s.remote' % branch)
                merge = self.repo.git.config('--get', 'branch.%s.merge' % branch).replace(
                    'refs/heads', remote)
            except git.GitCommandError:
                raise rpkgError('Branch {0} does not track remote branch.\n'
                                'Use the following command to fix that:\n'
                                '    git branch -u origin/REMOTE_BRANCH_NAME'.format(branch))
            if self.repo.git.rev_list('%s...%s' % (merge, branch)):
                raise rpkgError('There are unpushed changes in your repo')

    def check_inheritance(self, build_target, dest_tag):
        """Check if build tag inherits from dest tag"""
        ancestors = self.kojisession.getFullInheritance(
            build_target['build_tag'])
        ancestors = [ancestor['parent_id'] for ancestor in ancestors]
        if dest_tag['id'] not in [build_target['build_tag']] + ancestors:
            raise rpkgError(
                'Packages in destination tag %(dest_tag_name)s are not '
                'inherited by build tag %(build_tag_name)s' % build_target)

    def construct_build_url(self, repo_name=None, commit_hash=None):
        """Construct build URL with namespaced anongiturl and commit hash

        :param str repo_name: name of the repository part of the build URL. If
            omitted, namespaced name will be guessed from current repository.
            The given repository name will be used in URL directly without
            guessing namespace.
        :param str commit_hash: the commit hash appended to build URL. It
            omitted, the latest commit hash got from current repository will be
            used.
        :return: URL built from anongiturl.
        :rtype: str
        """
        return '{0}#{1}'.format(
            self._get_namespace_anongiturl(repo_name or self.ns_repo_name),
            commit_hash or self.commithash)

    def build(self, skip_tag=False, scratch=False, background=False,
              url=None, chain=None, arches=None, sets=False, nvr_check=True,
              fail_fast=False):
        """Initiate a build in build system

        :param bool skip_tag: Skip the tag action after the build.
        :param bool scratch: Perform a scratch build. Default is False.
        :param bool background: Perform the build with a low priority. Default
            is False.
        :param str url: A url to an uploaded srpm to build from.
        :param list arches: A set of arches to limit the scratch build for.
        :param list chain: A chain build set. Only used for chain build.
        :param bool sets: whether or not the chain has sets .
        :param bool nvr_check: locally construct NVR and submit a build only if
            NVR doesn't exist in a build system
        :param bool fail_fast: Perform the build in fast failure mode, which
            will cause the entire build to fail if any subtask/architecture
            build fails.
        :return: task ID returned from Koji API ``build`` and ``chainBuild``.
        :rtype: int
        """

        # Ensure the repo exists as well as repo data and site data
        # build up the command that a user would issue
        cmd = [self.build_client]

        # construct the url
        if not url:
            # We don't have a url, so build from the latest commit
            # Check to see if the tree is dirty and if all local commits
            # are pushed
            try:
                self.check_repo()
            except rpkgError as e:
                msg = '{0}\n{1}'.format(
                    str(e),
                    'Try option --srpm to make scratch build from local changes.')
                raise rpkgError(msg)
            url = self.construct_build_url()

        # Check to see if the target is valid
        build_target = self.kojisession.getBuildTarget(self.target)
        if not build_target:
            raise rpkgError('Unknown build target: %s' % self.target)
        # see if the dest tag is locked
        dest_tag = self.kojisession.getTag(build_target['dest_tag_name'])
        if not dest_tag:
            raise rpkgError('Unknown destination tag %s'
                            % build_target['dest_tag_name'])
        if dest_tag['locked'] and not scratch:
            raise rpkgError('Destination tag %s is locked' % dest_tag['name'])

        if chain:
            cmd.append('chain-build')
            # We're chain building, make sure inheritance works
            self.check_inheritance(build_target, dest_tag)
        else:
            cmd.append('build')

        # define our dictionary for options
        opts = {}
        # Set a placeholder for the build priority
        priority = None
        if skip_tag:
            opts['skip_tag'] = True
            cmd.append('--skip-tag')
        if scratch:
            opts['scratch'] = True
            cmd.append('--scratch')
        if background:
            cmd.append('--background')
            priority = 5  # magic koji number :/
        if fail_fast:
            opts['fail_fast'] = True
            cmd.append('--fail-fast')
        if arches:
            if not scratch:
                raise rpkgError('Cannot override arches for non-scratch '
                                'builds')
            for arch in arches:
                if not re.match(r'^[0-9a-zA-Z_.]+$', arch):
                    raise rpkgError('Invalid architecture name: %s' % arch)
            cmd.append('--arch-override=%s' % ','.join(arches))
            opts['arch_override'] = ' '.join(arches)

        cmd.append(self.target)

        if url.endswith('.src.rpm'):
            srpm = os.path.basename(url)
            build_reference = srpm
        else:
            try:
                build_reference = self.nvr
            except rpkgError as error:
                self.log.warning(error)
                if nvr_check:
                    self.log.info('Note: You can skip NVR construction & NVR'
                                  ' check with --skip-nvr-check. See help for'
                                  ' more info.')
                    raise rpkgError('Cannot continue without properly constructed NVR.')
                else:
                    self.log.info('NVR checking will be skipped so I do not'
                                  ' care that I am not able to construct NVR.'
                                  '  I will refer this build by package name'
                                  ' in following messages.')
                    build_reference = self.repo_name

        # See if this build has been done.  Does not check builds within
        # a chain, or if the %autorelease macro is used.
        if (nvr_check or self.uses_autorelease) and not scratch and not url.endswith('.src.rpm'):
            build = self.kojisession.getBuild(self.nvr)
            if build:
                if build['state'] == 1:
                    raise rpkgError('Package %s has already been built\n'
                                    'Note: You can skip this check with'
                                    ' --skip-nvr-check. See help for more'
                                    ' info.' % self.nvr)

        # Now submit the task and get the task_id to return
        # Handle the chain build version
        if chain:
            self.log.debug('Adding %s to the chain', url)
            # If we're dealing with build sets the behaviour of the last
            # package changes, and we add it to the last (potentially empty)
            # set.  Otherwise the last package just gets added to the end of
            # the chain.
            if sets:
                chain[-1].append(url)
            else:
                chain.append([url])
            # This next list comp is ugly, but it's how we properly get a :
            # put in between each build set
            cmd.extend(' : '.join(
                [' '.join(build_sets) for build_sets in chain]
            ).split())
            self.log.info('Chain building %s + %s for %s',
                          build_reference, chain[:-1], self.target)
            self.log.debug(
                'Building chain %s for %s with options %s and a priority '
                'of %s', chain, self.target, opts, priority)
            self.log.debug(' '.join(cmd))

            if self.dry_run:
                self.log.info(
                    'DRY-RUN: kojisession.chainBuild(%s, %s, %r, priority=%s)',
                    chain, self.target, opts, priority)
                task_id = random.randint(1000, 2000)
            else:
                task_id = self.kojisession.chainBuild(
                    chain, self.target, opts, priority=priority)

        # Now handle the normal build
        else:
            cmd.append(url)
            self.log.info('Building %s for %s', build_reference, self.target)
            self.log.debug(
                'Building %s for %s with options %s and a priority of %s',
                url, self.target, opts, priority)
            self.log.debug(' '.join(cmd))

            if self.dry_run:
                self.log.info(
                    'DRY-RUN: kojisession.build(%s, %s, %r, priority=%s)',
                    url, self.target, opts, priority)
                task_id = random.randint(1000, 2000)
            else:
                task_id = self.kojisession.build(
                    url, self.target, opts, priority=priority)

        self.log.info('Created task: %s', task_id)
        self.log.info('Task info: %s/taskinfo?taskID=%s',
                      self.kojiweburl, task_id)
        return task_id

    def clog(self, raw=False, subject=None):
        """Write the latest spec changelog entry to a clog file"""

        spec_file = os.path.join(self.path, self.spec)
        # TODO: remove when fixed
        # Command contains workaround (undefines _changelog_trimtime) described at:
        # https://github.com/rpm-software-management/rpm/issues/1301
        # It caused, that older changelog records were not displayed.
        cmd = ['rpm'] + self.rpmdefines + ['-q', '--qf', '"%{CHANGELOGTEXT}\n"',
                                           '--undefine', '"_changelog_trimtime"',
                                           '--specfile', '"%s"' % spec_file]
        proc = subprocess.Popen(' '.join(cmd), shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        stdout, stderr = proc.communicate()
        if proc.returncode > 0:
            raise rpkgError(stderr.strip())

        firstline = True
        if subject:
            clog_lines = [subject + "\n", "\n"]
        else:
            clog_lines = []
        buf = six.StringIO(stdout)
        for line in buf:
            if line == '\n' or line.startswith('$'):
                continue
            if line == '(none)\n':
                # (none) may appear as the last line in changelog got from SPEC
                # file. In some cases, e.g. there is only one changelog entry
                # in SPEC, no (none) line presents. Thus, when for loop ends, all
                # lines of changelog are handled.
                break
            if raw:
                clog_lines.append(line)
            else:
                clog_lines.append(line.replace('- ', '', 1))
            if firstline and not subject:
                # Add a newline after the first line to ensure that Git doesn't
                # concatenate them all as the subject.
                clog_lines.append("\n")
                firstline = False

        buf.close()

        # Now open the clog file and write out the lines
        with open(os.path.join(self.path, 'clog'), 'w') as clog:
            clog.writelines(clog_lines)

    def compile(self, arch=None, short=False, builddir=None, nocheck=False,
                define=None, extra_args=None):
        """Run rpmbuild -bc

        optionally for a specific arch, or short-circuit it,
        define an alternate builddir, or define some macro

        Logs the output and returns nothing
        """

        # setup the rpm command
        cmd = ['rpmbuild']
        cmd.extend(self.rpmdefines)
        if builddir:
            # Tack on a new builddir to the end of the defines
            cmd.append("--define '_builddir %s'" % os.path.abspath(builddir))
        if arch:
            cmd.extend(['--target', arch])
        if define:
            for entry in define:
                cmd.extend(['--define', entry])
        if extra_args:
            cmd.extend(extra_args)
            self.log.debug("Extra args '{0}' are passed to rpmbuild "
                           "command".format(extra_args))
        if short:
            cmd.append('--short-circuit')
        if nocheck:
            cmd.append('--nocheck')
        if self.quiet:
            cmd.append('--quiet')
        cmd.extend(['-bc', os.path.join(self.path, self.spec)])
        # Run the command
        self._run_command(cmd, shell=True)

    def giturl(self):
        """Return the git url that would be used for building"""
        self.check_repo(is_dirty=False, all_pushed=False)
        return self.construct_build_url()

    def koji_upload(self, file, path, callback=None, name=None):
        """Upload a file to koji

        file is the file you wish to upload

        path is the relative path on the server to upload to

        callback is the progress callback to use, if any

        name is an alternate upload file name to use on the server if specified,
            otherwise basename of local file will be used

        Returns nothing or raises
        """

        # See if we actually have a file
        if not os.path.exists(file):
            raise rpkgError('No such file: %s' % file)
        if not self.kojisession:
            raise rpkgError('No active %s session.' %
                            os.path.basename(self.build_client))
        # This should have a try and catch koji errors
        self.kojisession.uploadWrapper(file, path, name=name, callback=callback)

    def install(self, arch=None, short=False, builddir=None, nocheck=False,
                buildrootdir=None, define=None, extra_args=None):
        """Run ``rpmbuild -bi``

        optionally for a specific arch, short-circuit it,
        define an alternative builddir, or define rpmbuild macros

        Logs the output and returns nothing

        :param str arch: specify a specific arch.
        :param list define: specify a list of rpmbuild macros.
        :param bool short: short-circuit it.
        :param str builddir: alternate builddir.
        :param bool nocheck: do not check.
        :param str buildrootdir: alternate buildrootdir.
        :param list extra_args: additional arguments that are passed to
            the rpmbuild command.

        .. versionadded: 1.56
           Parameter buildrootdir.
        """

        # setup the rpm command
        cmd = ['rpmbuild']
        cmd.extend(self.rpmdefines)
        if builddir:
            # Tack on a new builddir to the end of the defines
            cmd.append("--define '_builddir %s'" % os.path.abspath(builddir))
        if arch:
            cmd.extend(['--target', arch])
        if define:
            for entry in define:
                cmd.extend(['--define', entry])
        if extra_args:
            cmd.extend(extra_args)
            self.log.debug("Extra args '{0}' are passed to rpmbuild "
                           "command".format(extra_args))
        if short:
            cmd.append('--short-circuit')
        if nocheck:
            cmd.append('--nocheck')
        if self.quiet:
            cmd.append('--quiet')
        if buildrootdir:
            cmd.append("--define '_buildrootdir {0}'".format(
                os.path.abspath(buildrootdir)))
        cmd.extend(['-bi', os.path.join(self.path, self.spec)])
        # Run the command
        self._run_command(cmd, shell=True)
        return

    def lint(self, info=False, rpmlintconf=None):
        """Run rpmlint over a built srpm

        Log the output and returns nothing
        rpmlintconf is the name of the config file passed to rpmlint if
        specified by the command line argument.
        """

        # Check for srpm
        srpm = "%s-%s-%s.src.rpm" % (self.repo_name, self.ver, self.rel)
        if not os.path.exists(os.path.join(self.path, srpm)):
            log.warning('No srpm found')

        # Get the possible built arches
        arches = set(self._get_build_arches_from_spec())
        rpms = set()
        for arch in arches:
            if os.path.exists(os.path.join(self.path, arch)):
                # For each available arch folder, lists file and keep
                # those ending with .rpm
                rpms.update(glob.glob(os.path.join(self.path, arch, '*.rpm')))
        if not rpms:
            log.warning('No rpm found')
        cmd = ['rpmlint']
        default_rpmlintconf = '{0}.rpmlintrc'.format(self.repo_name)
        if info:
            cmd.extend(['-i'])
        if rpmlintconf:
            cmd.extend(["-f", os.path.join(self.path, rpmlintconf)])
        elif os.path.isfile(os.path.join(self.path, default_rpmlintconf)):
            cmd.extend(["-f", os.path.join(self.path, default_rpmlintconf)])
        elif os.path.isfile(os.path.join(self.path, ".rpmlint")):
            self.log.warning('.rpmlint file usage as default rpmlint configuration is deprecated '
                             'Use {0} instead'.format(default_rpmlintconf))
        cmd.append(os.path.join(self.path, self.spec))
        if os.path.exists(os.path.join(self.path, srpm)):
            cmd.append(os.path.join(self.path, srpm))
        cmd.extend(sorted(rpms))
        # Run the command
        self._run_command(cmd, shell=True)

    def list_side_tags(self, base_tag=None, user=None):
        return self.kojisession.listSideTags(basetag=base_tag, user=user)

    def local(self, localargs, arch=None, hashtype=None, builddir=None,
              buildrootdir=None, define=None, extra_args=None):
        """rpmbuild locally for given arch.

        Takes localargs (passed to rpmbuild), arch to build for, and hashtype
        to build with.

        Writes output to a log file and logs it to the logger. Log file is
        written into current working directory and in format
        `.build-{version}-{release}.log`.

        :param str arch: to optionally build for a specific arch.
        :param list define: optional list of rpmbuild macros.
        :param str hashtype: an alternative algorithm used for payload file
            digests.
        :param str builddir: an alternative builddir.
        :param str buildrootdir: an alternative buildrootdir.
        :param list extra_args: additional arguments that are passed to
            the rpmbuild command.
        :raises rpkgError: if underlying `rpmbuild` fails.

        .. versionadded: 1.56
           Parameter buildrootdir.
        """

        # This could really use a list of arches to build for and loop over
        # Get the sources
        # build up the rpm command
        cmd = ['rpmbuild']
        cmd.extend(self.rpmdefines + localargs)
        if builddir:
            # Tack on a new builddir to the end of the defines
            cmd.append("--define '_builddir %s'" % os.path.abspath(builddir))
        if arch:
            cmd.extend(['--target', arch])
        if define:
            for entry in define:
                cmd.extend(['--define', entry])
        if extra_args:
            cmd.extend(extra_args)
            self.log.debug("Extra args '{0}' are passed to rpmbuild "
                           "command".format(extra_args))
        if self.quiet:
            cmd.append('--quiet')
        if buildrootdir:
            cmd.append("--define '_buildrootdir {0}'".format(
                os.path.abspath(buildrootdir)))
        # Figure out the hash type to use
        if not hashtype:
            # Try to determine the dist
            hashtype = self._guess_hashtype()
        # This may need to get updated if we ever change our checksum default
        if not hashtype == 'sha256':
            cmd.extend(["--define '_source_filedigest_algorithm %s'"
                        % hashtype,
                        "--define '_binary_filedigest_algorithm %s'"
                        % hashtype])
        specpath = os.path.join(self.path, self.spec)
        tmpdir = None
        try:
            if not self.uses_rpmautospec or not rpmautospec_process_distgit:
                cmd.extend(['-ba', specpath])
            else:
                tmpdir = tempfile.mkdtemp(prefix="rpkg-rpmautospec")
                tmpspecpath = os.path.join(tmpdir, self.spec)
                rpmautospec_process_distgit(specpath, tmpspecpath)
                cmd.extend(['-ba', tmpspecpath])
            logfile = '.build-%s-%s.log' % (self.ver, self.rel)

            cmd = '%s 2>&1 | tee %s' % (' '.join(cmd), logfile)
            try:
                # Since zsh is a widely used, which is supported by fedpkg
                # actually, pipestatus is for checking the first command when zsh
                # is used.
                subprocess.check_call(
                    '%s; exit "${PIPESTATUS[0]} ${pipestatus[1]}"' % cmd,
                    shell=True)
            except subprocess.CalledProcessError:
                raise rpkgError(cmd)
        finally:
            self._cleanup_tmp_dir(tmpdir)

    # Not to be confused with mockconfig the property
    def mock_config(self, target=None, arch=None):
        """Generate a mock config based on branch data.

        :param str target: an alternative build target, otherwise default build
            target will be used.
        :param str arch: an alternative arch, otherwise local system arch will
            be used.
        :return: the mock config content got from Koji.
        :rtype: str
        """

        # Figure out some things about ourself.
        if not target:
            target = self.target
        if not arch:
            arch = self.localarch

        # Figure out if we have a valid build target
        build_target = self.anon_kojisession.getBuildTarget(target)
        if not build_target:
            raise rpkgError('Unknown build target: %s\n'
                            'Consider using the --target option' % target)

        try:
            repoid = self.anon_kojisession.getRepo(
                build_target['build_tag_name'])['id']
        except Exception:
            raise rpkgError('Could not find a valid build repo')

        # Get build config for details about package manager
        build_config = self.anon_kojisession.getBuildConfig(
            build_target["build_tag_name"]
        )
        package_manager = build_config.get("extra", {}).get("mock.package_manager")
        module_hotfixes = build_config.get("extra", {}).get("mock.yum.module_hotfixes")

        # Generate the config
        config = koji.genMockConfig(
            '%s-%s' % (target, arch),
            arch,
            distribution=self.disttag,
            tag_name=build_target['build_tag_name'],
            repoid=repoid,
            topurl=self.topurl,
            package_manager=package_manager,
            module_hotfixes=module_hotfixes,
        )

        # Return the mess
        return(config)

    def _config_dir_other(self, config_dir, filenames=('site-defaults.cfg',
                                                       'logging.ini')):
        """Populates mock config directory with other necessary files

        If files are found in system config directory for mock they are copied
        to mock config directory defined as method's argument. Otherwise empty
        files are created.
        """
        for filename in filenames:
            system_filename = '/etc/mock/%s' % filename
            tmp_filename = os.path.join(config_dir, filename)
            if os.path.exists(system_filename):
                try:
                    shutil.copy2(system_filename, tmp_filename)
                except Exception as error:
                    raise rpkgError('Failed to create copy system config file'
                                    ' %s: %s' % (filename, error))
            else:
                try:
                    open(tmp_filename, 'w').close()
                except Exception as error:
                    raise rpkgError('Failed to create empty mock config'
                                    ' file %s: %s'
                                    % (tmp_filename, error))

    def _config_dir_basic(self, config_dir=None, root=None):
        """Setup directory with essential mock config

        If config directory doesn't exist it will be created. If temporary
        directory was created by this method and error occours during
        processing, temporary directory is removed. Otherwise it caller's
        responsibility to remove this directory.

        Returns used config directory
        """
        if not root:
            root = self.mockconfig
        if not config_dir:
            my_config_dir = tempfile.mkdtemp(prefix="%s." % root,
                                             suffix='mockconfig')
            config_dir = my_config_dir
            self.log.debug('New mock config directory: %s', config_dir)
        else:
            my_config_dir = None

        try:
            config_content = self.mock_config()
        except rpkgError as error:
            self._cleanup_tmp_dir(my_config_dir)
            raise rpkgError('Could not generate config file: %s'
                            % error)

        config_file = os.path.join(config_dir, '%s.cfg' % root)
        if not isinstance(config_content, six.text_type):
            config_content = config_content.decode('utf-8')
        try:
            with io.open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
        except IOError as error:
            self._cleanup_tmp_dir(my_config_dir)
            raise rpkgError('Could not write config file: %s' % error)

        return config_dir

    def _cleanup_tmp_dir(self, tmp_dir):
        """Tries to remove directory and ignores EEXIST error

        If occoured directory not exist error (EEXIST) it silently continue.
        Otherwise raise rpkgError exception."""
        if not tmp_dir:
            return
        try:
            shutil.rmtree(tmp_dir)
        except OSError as error:
            if error.errno != errno.ENOENT:
                raise rpkgError('Failed to remove temporary directory'
                                ' %s. Reason: %s.' % (tmp_dir, error))

    def mockbuild(self, mockargs=[], root=None, hashtype=None, shell=None):
        """Build the package in mock, using mockargs

        Log the output and returns nothing

        :param list mockargs: list of command line arguments which are passed
            mock.
        :param str root: chroot config name which is passed to mock ``-r``
            option.
        :param str hashtype: used to generate SRPM only if there is no SRPM
            generated before.
        :param bool shell: indicate whether to go into chroot.

        .. versionadded:: 1.56
           Parameter shell.
        """

        # Make sure we have an srpm to run on
        self.srpm(hashtype=hashtype)

        # setup the command
        cmd = ['mock']
        cmd.extend(mockargs)
        if self.quiet:
            cmd.append('--quiet')

        config_dir = None
        if not root:
            root = self.mockconfig
            chroot_cfg = '/etc/mock/%s.cfg' % root
            if not os.path.exists(chroot_cfg):
                self.log.debug('Mock config %s was not found. Going to'
                               ' request koji to create new one.', chroot_cfg)
                try:
                    config_dir = self._config_dir_basic(root=root)
                except rpkgError as error:
                    raise rpkgError('Failed to create mock config directory:'
                                    ' %s' % error)
                self.log.debug('Temporary mock config directory: %s', config_dir)
                try:
                    self._config_dir_other(config_dir)
                except rpkgError as error:
                    self._cleanup_tmp_dir(config_dir)
                    raise rpkgError('Failed to populate mock config directory:'
                                    ' %s' % error)
                cmd.extend(['--configdir', config_dir])

        cmd += ['-r', root, '--resultdir', self.mock_results_dir]

        if shell:
            cmd.append('--shell')
        else:
            cmd += ['--rebuild', self.srpmname]

        # Run the command
        try:
            self._run_command(cmd)
        finally:
            self.log.debug('Cleaning up mock temporary config directory: %s', config_dir)
            self._cleanup_tmp_dir(config_dir)

    def upload(self, files, replace=False, offline=False):
        """Upload source file(s) in the lookaside cache

        Both file `sources` and `.gitignore` will be updated with uploaded
        files, and added to index tree eventually.

        :param iterable files: an iterable of files to upload.
        :param bool replace: optionally replace the existing tracked sources.
            Defaults to `False`.
        :param bool offline: do all the steps except uploading into lookaside cache
        :raises rpkgError: if failed to add a file to file `sources`.
        """

        sourcesf = SourcesFile(self.sources_filename, self.source_entry_type,
                               replace=replace)
        gitignore = GitIgnore(os.path.join(self.path, '.gitignore'))
        all_files_already_uploaded = True

        for f in files:
            # TODO: Skip empty file needed?
            file_hash = self.lookasidecache.hash_file(f)
            file_basename = os.path.basename(f)

            try:
                sourcesf.add_entry(self.lookasidehash, file_basename,
                                   file_hash)
            except HashtypeMixingError as e:
                msg = '\n'.join([
                    'Can not upload a new source file with a %(newhash)s '
                    'hash, as the "%(sources)s" file contains at least one '
                    'line with a %(existinghash)s hash.', '',
                    'Please redo the whole "%(sources)s" file using:',
                    '    `%(arg0)s new-sources file1 file2 ...`']) % {
                        'newhash': e.new_hashtype,
                        'existinghash': e.existing_hashtype,
                        'sources': self.sources_filename,
                        'arg0': sys.argv[0],
                    }
                raise rpkgError(msg)

            gitignore.add('/%s' % file_basename)
            if is_file_tracked(f, self.path):  # need full file path
                raise rpkgError(
                    "Error: Attempting to upload a git tracked file '{0}'. Only upload files not "
                    "tracked by git. You can use 'git rm --cached' to untrack a file from git.\n"
                    "Hint: Use git for text files like the spec file, patches or helper scripts. "
                    "Use the lookaside cache for binary blobs, usually upstream source "
                    "tarballs.".format(f))
            try:
                self.lookasidecache.upload(
                    self.ns_repo_name if self.lookaside_namespaced else self.repo_name,
                    f, file_hash, offline=offline)
            except AlreadyUploadedError:
                pass
            else:
                all_files_already_uploaded = False

        sourcesf.write()
        gitignore.write()

        self.repo.index.add(['sources', '.gitignore'])

        if all_files_already_uploaded:
            raise AlreadyUploadedError('File already uploaded')

    def prep(self, arch=None, builddir=None, buildrootdir=None, define=None,
             extra_args=None):
        """Run ``rpmbuild -bp``

        :param str arch: optional to run prep section for a specific arch. By
            default, local system arch will be used.
        :param list define: an optional list of rpmbuild macros.
        :param str builddir: an alternative builddir.
        :param str buildrootdir: an alternative buildrootdir.
        :param list extra_args: additional arguments that are passed to
            the rpmbuild command.

        .. versionadded: 1.56
           Parameter buildrootdir.
        """

        # setup the rpm command
        cmd = ['rpmbuild']

        # When "prep" command is run on detached branch (rhbz#1907964)
        # Recreate with: "git checkout <commit_id>".
        # Before self.rpmdefines() executes self.load_branch_merge() and it
        # shows potential confusing message to user,
        # execute self.load_branch_merge() in advance and catch related
        # exception. Set branch to value (=current commit id) that won't match
        # any predefined branch pattern. This will lead to displaying better
        # message to user (user is recommended to use --release argument)
        try:
            self.load_branch_merge()
        except rpkgError:
            head = self.repo.head
            if head.is_detached:
                self._branch_merge = head.commit.hexsha  # current commit id
            else:
                raise

        cmd.extend(self.rpmdefines)
        if builddir:
            # Tack on a new builddir to the end of the defines
            cmd.append("--define '_builddir %s'" % os.path.abspath(builddir))
        if arch:
            cmd.extend(['--target', arch])
        if define:
            for entry in define:
                cmd.extend(['--define', entry])
        if extra_args:
            cmd.extend(extra_args)
            self.log.debug("Extra args '{0}' are passed to rpmbuild "
                           "command".format(extra_args))
        if self.quiet:
            cmd.append('--quiet')
        if buildrootdir:
            cmd.append("--define '_buildrootdir {0}'".format(
                os.path.abspath(buildrootdir)))
        cmd.extend(['--nodeps', '-bp', os.path.join(self.path, self.spec)])
        # Run the command
        self._run_command(cmd, shell=True)

    def srpm(self, hashtype=None, define=None, builddir=None, buildrootdir=None,
             arch=None, extra_args=None):
        """Create an srpm using hashtype from content

        Requires sources already downloaded. The generated SRPM file will be
        put into package repository directory.

        :param str hashtype: an alternative algorithm used for payload file
            digests.
        :param list define: an optional list of rpmbuild macros.
        :param str builddir: optionally define an alternate builddir.
        :param str buildrootdir: optionally define an alternate buildrootdir.
        :param str arch: optional to run prep section for a specific arch. By
            default, local system arch will be used.
        :param list extra_args: additional arguments that are passed to
            the rpmbuild command.
        """

        self.srpmname = os.path.join(self.layout.srcrpmdir,
                                     "%s-%s-%s.src.rpm"
                                     % (self.repo_name, self.ver, self.rel))

        # See if we need to build the srpm
        if os.path.exists(self.srpmname):
            self.log.debug('Srpm found, rewriting it.')

        cmd = ['rpmbuild']
        cmd.extend(self.rpmdefines)
        if builddir:
            # Tack on a new builddir to the end of the defines
            cmd.append("--define '_builddir %s'" % os.path.abspath(builddir))
        if arch:
            cmd.extend(['--target', arch])
        if define:
            for entry in define:
                cmd.extend(['--define', entry])
        if extra_args:
            cmd.extend(extra_args)
            self.log.debug("Extra args '{0}' are passed to rpmbuild "
                           "command".format(extra_args))
        if self.quiet:
            cmd.append('--quiet')
        if buildrootdir:
            cmd.append("--define '_buildrootdir {0}'".format(
                os.path.abspath(buildrootdir)))

        # Figure out which hashtype to use, if not provided one
        if not hashtype:
            # Try to determine the dist
            hashtype = self._guess_hashtype()
        # This may need to get updated if we ever change our checksum default
        if not hashtype == 'sha256':
            cmd.extend(["--define '_source_filedigest_algorithm %s'"
                        % hashtype,
                        "--define '_binary_filedigest_algorithm %s'"
                        % hashtype])
        specpath = os.path.join(self.path, self.spec)
        tmpdir = None
        try:
            if not self.uses_rpmautospec or not rpmautospec_process_distgit:
                cmd.extend(['--nodeps', '-bs', specpath])
            else:
                tmpdir = tempfile.mkdtemp(prefix="rpkg-rpmautospec")
                tmpspecpath = os.path.join(tmpdir, self.spec)
                rpmautospec_process_distgit(specpath, tmpspecpath)
                cmd.extend(['--nodeps', '-bs', tmpspecpath])
            self._run_command(cmd, shell=True)
        finally:
            self._cleanup_tmp_dir(tmpdir)

    def unused_patches(self):
        """Discover patches checked into source control that are not used

        :return: a list of unused patches, which may be empty.
        :rtype: list
        """

        # Create a list for unused patches
        unused = []
        # Get the content of spec into memory for fast searching
        with open(os.path.join(self.path, self.spec), 'r') as f:
            data = f.read()
        if six.PY2:
            try:
                spec = data.decode('UTF-8')
            except UnicodeDecodeError as error:
                # when can't decode file, ignore chars and show warning
                spec = data.decode('UTF-8', 'ignore')
                line, offset = self._byte_offset_to_line_number(spec, error.start)
                self.log.warning("'%s' codec can't decode byte in position %d:%d : %s",
                                 error.encoding, line, offset, error.reason)
        else:
            spec = data
        # Replace %{name} with the package name
        spec = spec.replace("%{name}", self.repo_name)
        # Replace %{version} with the package version
        spec = spec.replace("%{version}", self.ver)

        # Get a list of files tracked in source control
        files = self.repo.git.ls_files('--exclude-standard').split()
        for file in files:
            # throw out non patches
            if not file.endswith(('.patch', '.diff')):
                continue
            if file not in spec:
                unused.append(file)
        return unused

    def _byte_offset_to_line_number(self, text, offset):
        """
        Convert byte offset (given by e.g. `DecodeError`) to human readable
        format (line number and char position)

        :return: a pair of line number and char offset.
        :rtype: list(int, int)
        """
        offset_inc = 0
        line_num = 1
        for line in text.split('\n'):
            if offset_inc + len(line) + 1 > offset:
                break
            else:
                offset_inc += len(line) + 1
                line_num += 1
        return [line_num, offset - offset_inc + 1]

    def verify_files(self, builddir=None, buildrootdir=None, define=None,
                     extra_args=None):
        """Run `rpmbuild -bl` to verify the `%files` section

        :param list define: an optional list of rpmbuild macros.
        :param str builddir: optionally define an alternate builddir.
        :param str buildrootdir: optionally define an alternate buildrootdir.
        :param list extra_args: additional arguments that are passed to
            the rpmbuild command.

        .. versionadded:: 1.56
           Parameter buildrootdir.
        """

        # setup the rpm command
        cmd = ['rpmbuild']
        cmd.extend(self.rpmdefines)
        if builddir:
            # Tack on a new builddir to the end of the defines
            cmd.append("--define '_builddir %s'" % os.path.abspath(builddir))
        if define:
            for entry in define:
                cmd.extend(['--define', entry])
        if extra_args:
            cmd.extend(extra_args)
            self.log.debug("Extra args '{0}' are passed to rpmbuild "
                           "command".format(extra_args))
        if self.quiet:
            cmd.append('--quiet')
        if buildrootdir:
            cmd.append("--define '_buildrootdir {0}'".format(
                os.path.abspath(buildrootdir)))
        cmd.extend(['-bl', os.path.join(self.path, self.spec)])
        # Run the command
        self._run_command(cmd, shell=True)

    def _process_koji_task_result(self, task_id):
        """
        Parse and modify output from brew/koji containing information about
        task (and eventually builds).

        :param int task_id: id of the current task
        :return: record containing information about repositories, builds and nvrs
        :rtype: dict(str, str)
        """
        koji_result = self.kojisession.getTaskResult(task_id)
        if not koji_result:
            raise rpkgError('Unknown task: %s' % task_id)
        koji_builds = koji_result.get("koji_builds", [])
        koji_result["koji_builds"] = []

        for build_id in koji_builds:
            try:
                build_id = int(build_id)
            except ValueError:
                raise rpkgError("Can not convert 'build_id' to integer: %s" % build_id)

            bdata = self.kojisession.getBuild(build_id)
            if not bdata:
                raise rpkgError('Unknown build: %s' % build_id)
            nvr = bdata.get("nvr")
            if nvr:
                koji_result.setdefault("nvrs", []).append(nvr)

            koji_result["koji_builds"].append(
                "%s/buildinfo?buildID=%d" % (self.kojiweburl, build_id))

        return koji_result

    def container_build_koji(self, target_override=False, opts={},
                             kojiprofile=None,
                             build_client=None,
                             koji_task_watcher=None,
                             nowait=False,
                             flatpak=False):

        # check if repo is dirty and all commits are pushed
        self.check_repo()
        container_target = self.target if target_override \
            else self.flatpak_build_target if flatpak \
            else self.container_build_target

        koji_session_backup = (self.build_client, self.kojiprofile)

        rv = 0  # return value of koji task. It is returned as a method result.
        try:
            self.load_kojisession()
            if "buildContainer" not in self.kojisession.system.listMethods():
                raise RuntimeError("Kojihub instance does not support buildContainer")

            build_target = self.kojisession.getBuildTarget(container_target)
            if not build_target:
                msg = "Unknown build target: %s" % container_target
                self.log.error(msg)
                raise UnknownTargetError(msg)
            else:
                dest_tag = self.kojisession.getTag(build_target['dest_tag'])
                if not dest_tag:
                    self.log.error("Unknown destination tag: %s", build_target['dest_tag_name'])
                if dest_tag['locked'] and 'scratch' not in opts:
                    self.log.error("Destination tag %s is locked", dest_tag['name'])

            source = self.construct_build_url()

            task_opts = {}
            for key in ('scratch', 'name', 'version', 'release', 'isolated',
                        'koji_parent_build', 'yum_repourls', 'git_branch',
                        'signing_intent', 'compose_ids', 'skip_build',
                        'dependency_replacements'):
                if key in opts:
                    task_opts[key] = opts[key]

            scratch = opts.get('scratch')
            arches = opts.get('arches')
            isolated = opts.get('isolated')
            if arches:
                if not (scratch or isolated):
                    raise rpkgError('Cannot override arches for non-scratch and non-isolated '
                                    'builds')
                task_opts['arch_override'] = ' '.join(arches)

            if flatpak:
                task_opts['flatpak'] = True

            priority = opts.get("priority", None)
            task_id = self.kojisession.buildContainer(source,
                                                      container_target,
                                                      task_opts,
                                                      priority=priority)
            self.log.info('Created task: %s', task_id)
            self.log.info('Task info: %s/taskinfo?taskID=%s', self.kojiweburl, task_id)
            if not nowait:
                rv = koji_task_watcher(self.kojisession, [task_id])
                if rv == 0:
                    result = self._process_koji_task_result(task_id)
                    log_result(self.log.info, result)

        finally:
            self.build_client, self.kojiprofile = koji_session_backup
            self.load_kojisession()

        return rv

    def container_build_setup(self, get_autorebuild=None,
                              set_autorebuild=None):
        cfp = ConfigParser()
        if os.path.exists(self.osbs_config_filename):
            cfp.read(self.osbs_config_filename)

        if get_autorebuild is not None:
            if not cfp.has_option('autorebuild', 'enabled'):
                self.log.info('false')
            else:
                self.log.info('true' if cfp.getboolean('autorebuild', 'enabled') else 'false')
        elif set_autorebuild is not None:
            if not cfp.has_section('autorebuild'):
                cfp.add_section('autorebuild')

            cfp.set('autorebuild', 'enabled', set_autorebuild)
            with open(self.osbs_config_filename, 'w') as fp:
                cfp.write(fp)

            self.repo.index.add([self.osbs_config_filename])
            self.log.info("Config value changed, don't forget to commit %s file",
                          self.osbs_config_filename)
        else:
            self.log.info('Nothing to be done')

    def copr_build(self, project, srpm_name, nowait, config_file):
        cmd = ['copr-cli']
        if config_file:
            cmd.extend(['--config', config_file])
        cmd.append('build')
        if nowait:
            cmd.append('--nowait')
        cmd.extend([project, srpm_name])
        self._run_command(cmd)

    def remove_side_tag(self, tag):
        self.kojisession.removeSideTag(tag)

    def request_side_tag(self, base_tag=None, suffix=None):
        if not base_tag:
            build_target = self.kojisession.getBuildTarget(self.target)
            if not build_target:
                raise rpkgError("Unknown build target: %s" % self.target)
            base_tag = build_target["build_tag_name"]

        kwargs = {}
        if suffix:
            kwargs["suffix"] = suffix

        return self.kojisession.createSideTag(base_tag, **kwargs)

    def is_retired(self):
        """
        Checks whether package or module is already retired.
        The state is indicated by present of files 'dead.package'
        or 'dead.module'.
        """
        return self.layout.is_retired()

    def retire(self, message):
        """Delete all tracked files and commit a new dead.package file for rpms
        or dead.module file for modules.

        Use optional message in commit.

        Runs the commands and returns nothing
        """
        if self.ns in self.block_retire_ns:
            raise rpkgError('Retirement not allowed in the %s namespace.'
                            ' Please check for documentation describing the'
                            ' proper policies and process.'
                            % self.ns)

        if self.ns in ('modules'):
            marker = 'dead.module'
        else:
            marker = 'dead.package'

        cmd = ['git']
        if self.quiet:
            cmd.append('--quiet')
        cmd.extend(['rm', '-rf', '.'])
        self._run_command(cmd, cwd=self.path)

        fd = open(os.path.join(self.path, marker), 'w')
        fd.write(message + '\n')
        fd.close()

        cmd = ['git', 'add', os.path.join(self.path, marker)]
        self._run_command(cmd, cwd=self.path)

        self.commit(message=message)

    def module_build_cancel(self, build_id, auth_method,
                            oidc_id_provider=None, oidc_client_id=None,
                            oidc_client_secret=None, oidc_scopes=None):
        """
        Cancel an MBS build

        :param int build_id: build ID to cancel
        :param str auth_method: authentication method used by the MBS
        :kwarg str oidc_id_provider: the OIDC provider when MBS is using OIDC
            for authentication
        :param str oidc_client_id: the OIDC client ID when MBS is using OIDC
            for authentication
        :param str oidc_client_secret: the OIDC client secret when MBS is using
            OIDC for authentication. Based on the OIDC setup, this could be
            `None`.
        :param list oidc_scopes: a list of OIDC scopes when MBS is using OIDC
            for authentication
        """
        # Make sure the build they are trying to cancel exists
        self.module_get_build(build_id)
        url = self.module_get_url(build_id, action='PATCH')
        resp = self.module_send_authorized_request(
            'PATCH', url, {'state': 'failed'}, auth_method, oidc_id_provider,
            oidc_client_id, oidc_client_secret, oidc_scopes, timeout=60)
        if not resp.ok:
            try:
                error_msg = resp.json()['message']
            except (ValueError, KeyError):
                error_msg = resp.text
            raise rpkgError(
                'The cancellation of module build #{0} failed with:\n{1}'
                .format(build_id, error_msg))

    def module_build_info(self, build_id):
        """
        Show information about an MBS build

        :param int build_id: build ID to query MBS about
        """
        # Load the Koji session anonymously so we get access to the Koji web
        # URL
        self.load_kojisession(anon=True)
        state_names = self.module_get_koji_state_dict()
        data = self.module_get_build(build_id)
        print('Name:           {0}'.format(data['name']))
        print('Stream:         {0}'.format(data['stream']))
        print('Version:        {0}'.format(data['version']))
        print('Scratch:        {0}'.format(data.get('scratch', False)))
        print('Koji Tag:       {0}'.format(data['koji_tag']))
        print('Owner:          {0}'.format(data['owner']))
        print('State:          {0}'.format(data['state_name']))
        print('State Reason:   {0}'.format(data['state_reason'] or ''))
        print('Time Submitted: {0}'.format(data['time_submitted']))
        print('Time Completed: {0}'.format(data['time_completed']))
        print('Components:')
        for package_name, task_data in data['tasks'].get('rpms', {}).items():
            koji_task_url = ''
            if task_data.get('task_id'):
                koji_task_url = '{0}/taskinfo?taskID={1}'.format(
                    self.kojiweburl, task_data['task_id'])
            print('    Name:       {0}'.format(package_name))
            print('    NVR:        {0}'.format(task_data['nvr']))
            print('    State:      {0}'.format(
                state_names[task_data.get('state', None)]))
            print('    Koji Task:  {0}\n'.format(koji_task_url))

    def module_get_build(self, build_id):
        """
        Get an MBS build
        :param build_id: an integer of the build ID to query MBS about
        :return: None or a dictionary representing the module build
        """
        url = self.module_get_url(build_id)
        response = requests.get(url, timeout=60)
        if response.ok:
            return response.json()
        else:
            try:
                error_msg = response.json()['message']
            except (ValueError, KeyError):
                error_msg = response.text
            raise rpkgError(
                'The following error occurred while getting information on '
                'module build #{0}:\n{1}'.format(build_id, error_msg))

    def module_get_latest_build(self, nsvc):
        """
        Get the latest MBS build for a particular module. If the module is
        built with multiple contexts, a random one will be returned.

        :param nsvc: a NAME:STREAM:VERSION:CONTEXT to filter the query
               (may be partial - e.g. only NAME or only NAME:STREAM)
        :return: the latest build
        """
        url = self.module_get_url(None)
        params = {
            'nsvc': nsvc,
            'order_desc_by': 'version',
            'per_page': 1
        }

        response = requests.get(url, timeout=60, params=params)
        if response.ok:
            j = response.json()
            if len(j['items']) == 0:
                return None
            else:
                return j['items'][0]
        else:
            try:
                error_msg = response.json()['message']
            except (ValueError, KeyError):
                error_msg = response.text
            raise rpkgError(
                'The following error occurred while getting information on '
                'module #{0}:\n{1}'.format(nsvc, error_msg))

    def module_get_url(self, build_id, action='GET', verbose=True):
        """
        Get the proper MBS API URL for the desired action

        :param int build_id: an integer of the module build desired. If this is
            set to None, then the base URL for all module builds is returned.
        :param str action: a string determining the HTTP action. If this is set
            to `GET`, then the URL will contain `?verbose=true`. Any other
            value will not have verbose set.
        :return: a string of the desired MBS API URL.
        :rtype: str
        """
        url = urljoin(self.module_api_url, 'module-builds/')
        if build_id is not None:
            url = '{0}{1}'.format(url, build_id)
        else:
            url = '{0}'.format(url)

        if action == 'GET':
            if verbose:
                url = '{0}?verbose=true'.format(url)
        return url

    @staticmethod
    def module_get_koji_state_dict():
        """
        Get a dictionary of Koji build states with the keys being strings and
        the values being their associated integer.

        :return: a dictionary of Koji build states
        :rtype: dict
        """
        state_names = dict([(v, k) for k, v in koji.BUILD_STATES.items()])
        state_names[None] = 'undefined'
        return state_names

    def module_get_scm_info(self, scm_url=None, branch=None, check_repo=True):
        """
        Determines the proper SCM URL and branch based on the arguments. If the
        user doesn't specify an SCM URL and branch, then the git repo the user
        is currently in is used instead.

        :param str scm_url: a string of the module's SCM URL
        :param str branch: a string of the module's branch
        :kwarg bool check_repo: a boolean that determines if check_repo should
            be run when an scm_url is not provided.
        :return: a tuple containing a string of the SCM URL and a string of the
            branch
        :rtype: tuple
        """
        if not scm_url and check_repo:
            # Make sure the local repo is clean (no unpushed changes) if the
            # user didn't specify an SCM URL
            self.check_repo()

        if branch:
            actual_branch = branch
        else:
            # If the branch wasn't specified, make sure they also didn't
            # specify an scm_url
            if scm_url:
                raise rpkgError('You need to specify a branch if you specify '
                                'the SCM URL')
            # If the scm_url was not specified, then just use the active
            # branch
            actual_branch = self.repo.active_branch.name

        if scm_url:
            actual_scm_url = scm_url
        else:
            # If the scm_url isn't specified, get the remote git URL of the
            # git repo the current user is in
            actual_scm_url = self._get_namespace_anongiturl(
                self.ns_repo_name)
            actual_scm_url = '{0}?#{1}'.format(actual_scm_url, self.commithash)
        return actual_scm_url, actual_branch

    def module_local_build(self, file_path, stream, local_builds_nsvs=None, verbose=False,
                           debug=False, skip_tests=False, mbs_config=None,
                           mbs_config_section=None, default_streams=None,
                           offline=False, base_module_repositories=None,
                           srpms=None):
        """
        A wrapper for `mbs-manager build_module_locally`.

        :param str file_path: a string, path of the module's modulemd yaml file.
        :param str stream: a string, stream of the module.
        :param list local_builds_nsvs: a list of localbuild ids to import into
            MBS before running this local build.
        :param bool verbose: a boolean specifying if mbs-manager should be
            verbose. This is overridden by self.quiet.
        :param bool debug: a boolean specifying if mbs-manager should be debug.
            This is overridden by self.quiet and verbose.
        :param bool skip_tests: a boolean determining if the check sections
            should be skipped.
        :param str mbs_config: a string, path to alternative MBS config file to
            use.
        :param str mbs_config_section: a string, name of alternative config
            section to use.
        :param default_streams: a list, contains strings with default
            `name:stream` pairs which are passed to mbs-manager using the '-s'
            command line argument.
        :type default_streams: list[str]
        :param bool offline: when True, the module is built offline without
            accessing any external infrastructure.
        :param list base_module_repositories: a list of full paths to local
            .repo files defining the repositories for base module when
            building with offline set to True.
        :param srpms: a list, contains strings with paths to SRPMs to override
            components from distgit when building module.
        :type srpms: list[str]
        :return: None
        """
        command = ['mbs-manager']
        if self.quiet:
            command.append('-q')
        elif verbose:
            command.append('-v')
        elif debug:
            command.append('-d')
        command.append('build_module_locally')

        if local_builds_nsvs:
            for nsv in local_builds_nsvs:
                command += ['--add-local-build', nsv]

        if skip_tests:
            command.append('--skiptests')

        if offline:
            command.append('--offline')

        if base_module_repositories:
            for repo in base_module_repositories:
                command.extend(['-r', repo])

        command.extend(['--file', file_path])
        command.extend(['--stream', stream])

        if default_streams:
            for name_stream in default_streams:
                command.extend(['-s', name_stream])

        if srpms:
            for srpm in srpms:
                command.extend(['--srpm', srpm])

        env = {}
        if mbs_config:
            env['MBS_CONFIG_FILE'] = mbs_config
        if mbs_config_section:
            env['MBS_CONFIG_SECTION'] = mbs_config_section

        try:
            self._run_command(command, env=env)
        except rpkgError as e:
            # If the exception wraps another one which has .errno == ENOENT
            # this indicates that the file (mbs-manager executable) wasn't
            # found. This works in both Python 2 and 3 which throw different
            # types of exceptions in this case. We use duck-typing rather than
            # checking for the respective specific exception types because the
            # Python 3 FileNotFoundError exception isn't known in Python 2 and
            # special casing this makes the code unnecessarily complicated.
            e_errno = None
            if e.args and isinstance(e.args[0], Exception):
                e_errno = getattr(e.args[0], 'errno', None)
            if (e_errno == errno.ENOENT
                    or str(e) == '[Errno 2] No such file or directory'):
                raise rpkgError('mbs-manager is missing. Please install '
                                'module-build-service.')
            else:
                raise

    def module_overview(self, limit=10, finished=True, owner=None):
        """
        Show the overview of the latest builds in MBS

        :param int limit: an integer of the number of most recent module builds
            to display. This defaults to 10.
        :param bool finished: a boolean that determines if only finished or
            unfinished module builds should be displayed. This defaults to True.
        :param str owner: list only builds of that user.
        """
        # Don't let the user cause problems by specifying a negative limit
        if limit < 1:
            limit = 1
        build_states = {
            'init': 0,
            'wait': 1,
            'build': 2,
            'done': 3,
            'failed': 4,
            'ready': 5,
        }
        baseurl = self.module_get_url(build_id=None)
        if finished:
            # These are the states when a build is finished
            states = [build_states['done'], build_states['ready'],
                      build_states['failed']]
        else:
            # These are the states when a build is in progress
            states = [build_states['init'], build_states['wait'],
                      build_states['build']]

        def _get_module_builds(state, owner=None):
            """
            Private function that is used for multithreading later on to get
            the desired amount of builds for a specific state.

            :param state: an integer representing the build state to query for
            :param owner: a string; to query for that owner's builds
            :return: a generator to yield dictionaries of the builds found
            """
            total = 0
            page = 1
            # If the limit is above 100, we don't want the amount of results
            # per_page to exceed 100 since this is not allowed.
            per_page = min(limit, 100)
            params = {
                'state': state,
                # Order by the latest builds first
                'order_desc_by': 'id',
                'verbose': True,
                'per_page': per_page
            }
            if owner:
                params['owner'] = owner
            while total < limit:
                params['page'] = page
                response = requests.get(baseurl, params=params, timeout=30)
                if not response.ok:
                    try:
                        error = response.json()['message']
                    except (ValueError, KeyError):
                        error = response.text
                    raise rpkgError(
                        'The request to "{0}" failed with parameters "{1}". '
                        'The status code was "{2}". The error was: {3}'
                        .format(baseurl, str(params), response.status_code,
                                error))

                data = response.json()
                for item in data['items']:
                    total += 1
                    yield item

                if data['meta']['next']:
                    page += 1
                else:
                    # Even if we haven't reached the desired amount of builds,
                    # we must break out of the loop because we are out of pages
                    # to search
                    break

        # Make this one thread per state we want to query
        pool = ThreadPool(3)
        # Eventually, the MBS should support a range of states but for now, we
        # have to be somewhat wasteful and query per state
        module_builds = pool.map(
            lambda x: list(_get_module_builds(state=x, owner=owner)), states)
        # Make one flat list with all the modules
        module_builds = [item for sublist in module_builds for item in sublist]
        # Sort the list with a secondary key first. It should prevent the situation
        # that two builds with same id (its status was changed during the queries)
        # are in the list and the record with older status is removed.
        module_builds.sort(key=lambda x: x['time_modified'], reverse=True)
        # Sort the list of builds to be oldest to newest
        module_builds.sort(key=lambda x: x['id'])
        # Only grab the desired limit starting from the newest builds
        module_builds = module_builds[(limit * -1):]
        # Track potential duplicates if the state changed in the middle of the
        # query
        module_build_ids = set()
        for build in module_builds:
            if build['id'] in module_build_ids:
                continue
            module_build_ids.add(build['id'])
            print('ID:       {0}'.format(build['id']))
            print('Name:     {0}'.format(build['name']))
            print('Stream:   {0}'.format(build['stream']))
            print('Version:  {0}'.format(build['version']))
            print('Scratch:  {0}'.format(build.get('scratch', False)))
            print('Koji Tag: {0}'.format(build['koji_tag']))
            print('Owner:    {0}'.format(build['owner']))
            print('State:    {0}\n'.format(build['state_name']))

    def module_send_authorized_request(self, verb, url, body, auth_method,
                                       oidc_id_provider=None,
                                       oidc_client_id=None,
                                       oidc_client_secret=None,
                                       oidc_scopes=None, **kwargs):
        """
        Sends authorized request to MBS

        :param str verb: a string of the HTTP verb of the request (e.g. `POST`)
        :param str url: a string of the URL to make the request on.
        :param dict body: a dictionary of the data to send in the authorized
            request.
        :param str auth_method: a string of the authentication method used by
            the MBS. Valid methods are `oidc` and `kerberos`.
        :param str oidc_id_provider: a string of the OIDC provider when MBS is
            using OIDC for authentication
        :param str oidc_client_id: a string of the OIDC client ID when MBS is
            using OIDC for authentication
        :param str oidc_client_secret: a string of the OIDC client secret when
            MBS is using OIDC for authentication. Based on the OIDC setup, this
            could be None.
        :param list oidc_scopes: a list of OIDC scopes when MBS is using OIDC
            for authentication
        :param kwargs: any additional python-requests keyword arguments.
        :return: a python-requests response object
        """
        if auth_method == 'oidc':
            import openidc_client
            if oidc_id_provider is None or oidc_client_id is None or \
                    oidc_scopes is None:
                raise ValueError('The selected authentication method was '
                                 '"oidc" but the OIDC configuration keyword '
                                 'arguments were not specified')

            mapping = {'Token': 'Token', 'Authorization': 'Authorization'}
            # Get the auth token using the OpenID client
            oidc = openidc_client.OpenIDCClient(
                'mbs_build', oidc_id_provider, mapping, oidc_client_id,
                oidc_client_secret)

            resp = oidc.send_request(
                url, http_method=verb.upper(), json=body, scopes=oidc_scopes,
                **kwargs)
        elif auth_method == 'kerberos':
            import requests_kerberos

            if type(body) is dict:
                data = json.dumps(body)
            else:
                data = body
            auth = requests_kerberos.HTTPKerberosAuth(
                mutual_authentication=requests_kerberos.OPTIONAL)
            resp = requests.request(verb, url, data=data, auth=auth, **kwargs)
            if resp.status_code == 401:
                raise rpkgError('MBS authentication using Kerberos failed. '
                                'Make sure you have a valid Kerberos ticket.')
        else:
            # This scenario should not be reached because the config was
            # validated in the function that calls this function
            raise rpkgError('An unsupported MBS "auth_method" was provided')
        return resp

    def module_submit_build(self, scm_url, branch, auth_method,
                            buildrequires=None, requires=None, optional=None,
                            oidc_id_provider=None, oidc_client_id=None,
                            oidc_client_secret=None, oidc_scopes=None,
                            scratch=False, modulemd=None, srpms=[]):
        """
        Submit a module build to the MBS

        :param scm_url: a string of the module's SCM URL
        :param branch: a string of the module's branch
        :param str auth_method: a string of the authentication method used by
            the MBS.
        :param list buildrequires: a list of buildrequires in the format of
            'name:stream' to override.
        :param list requires: a list of requires in the format of 'name:stream'
            to override.
        :param list optional: an optional list of tuples (key, value) to be
            passed in with the MBS build submission.
        :type optional: list[str]
        :param str oidc_id_provider: a string of the OIDC provider when MBS is
            using OIDC for authentication.
        :param str oidc_client_id: a string of the OIDC client ID when MBS is
            using OIDC for authentication
        :param str oidc_client_secret: a string of the OIDC client secret when
            MBS is using OIDC for authentication. Based on the OIDC setup, this
            could be None. :kwarg oidc_scopes: a list of OIDC scopes when MBS
            is using OIDC for authentication.
        :param bool scratch: optionally perform a scratch module build,
            default is `False`.
        :param str modulemd: a string, path of the module's modulemd yaml file
            to use for a scratch build.
        :param srpms: a list of koji upload links for SRPMs to use for a scratch
            build.
        :type srpms: list[str]
        :return: a list of module build IDs that are being built from this
            request.
        :rtype: list[int]
        """
        body = {'scmurl': scm_url, 'branch': branch, 'scratch': scratch}
        optional = optional if optional else []
        optional_dict = {}
        for option in optional:
            key, value = option
            optional_dict[key] = value

        for dep_type, overrides in (('buildrequires', buildrequires),
                                    ('requires', requires)):
            for override in overrides or []:
                dep_name, dep_stream = override
                # Get the override key that MBS accepts (e.g.
                # buildrequire_overrides)
                key = '{0}_overrides'.format(dep_type[:-1])
                body.setdefault(key, {})
                body[key].setdefault(dep_name, [])
                body[key][dep_name].append(dep_stream)

        body.update(optional_dict)

        if modulemd:
            with open(modulemd, 'rb') as mmd_file:
                mmd_content = mmd_file.read().decode('utf-8')
            body['modulemd'] = mmd_content
            body['module_name'] = str(os.path.splitext(os.path.basename(modulemd))[0])
        if srpms:
            body['srpms'] = srpms

        url = self.module_get_url(build_id=None, action='POST')
        resp = self.module_send_authorized_request(
            'POST', url, body, auth_method, oidc_id_provider, oidc_client_id,
            oidc_client_secret, oidc_scopes, timeout=120)

        if not resp.ok:
            try:
                data = resp.json()
            except ValueError:
                raise rpkgError(
                    'The build failed with an unexpected error: %s' % resp.text
                )
            if 'message' in data:
                error_msg = data['message']
            else:
                error_msg = resp.text
            raise rpkgError('The build failed with:\n{0}'.format(error_msg))
        data = resp.json()
        builds = data if isinstance(data, list) else [data]
        return [build['id'] for build in builds]

    @staticmethod
    def stats_module_build_components(build_info):
        stats_key_mapping = {
            koji.BUILD_STATES['BUILDING']: 'building',
            koji.BUILD_STATES['COMPLETE']: 'done',
            koji.BUILD_STATES['FAILED']: 'failed',
        }

        stats = {
            'building': 0,
            'done': 0,
            'failed': 0,
            'total': 0,
            'completion_percentage': 0
        }

        for task_state, task_infos in build_info['tasks']['rpms'].items():
            assert isinstance(task_infos, list)
            n = len(task_infos)
            stats['total'] += n
            if task_state not in stats_key_mapping:
                continue
            stats[stats_key_mapping[task_state]] = n
        stats['completion_percentage'] = \
            int(float(stats['done'] + stats['failed']) / stats['total'] * 100) \
            if stats['total'] > 0 else 100  # to avoid zero division when there were no task_infos
        return stats

    def get_watched_module_builds(self, build_ids):
        # Limit the number of threads to an arbitrary 8,
        # to avoid starting too many threads when running in a
        # container in the cloud.
        pool = ThreadPool(min(8, len(build_ids) or 1))
        while True:
            module_builds = pool.map(self.module_get_build, build_ids)

            for module_build in module_builds:
                # Remove ?verbose=True because modulemd is not necessary for watch
                module_build['link'] = \
                    self.module_get_url(module_build['id']).split('?')[0]

                # tasks/rpms is a mapping from package name to package info,
                # e.g. {'pkg': {'nvr': ..., 'task_id': ..., 'state': ...}}
                # The injected task info will look like:
                # {'pkg': ..., 'nvr': ..., 'task_id': ..., 'state': ...}

                # Inject package name into task info and replace None state
                # with -1 so that None does not impact the comparison for
                # sort.
                formatted_tasks = []
                for pkg_name, task_info in module_build['tasks'].get('rpms', {}).items():
                    new_task_info = task_info.copy()
                    new_task_info['package_name'] = pkg_name
                    if new_task_info['state'] is None:
                        new_task_info['state'] = -1
                    formatted_tasks.append(new_task_info)

                # Group rpms by task state for later accessing RPMs info by
                # state easily. Calculating statistics depends on it.
                formatted_tasks = sorted(formatted_tasks, key=itemgetter('state'))

                # The final result is a mapping from Koji task state to
                # list of task info mappings.
                module_build['tasks']['rpms'] = dict(
                    (task_state, sorted(data, key=itemgetter('package_name')))
                    for task_state, data in groupby(
                        formatted_tasks, itemgetter('state'))
                )

                module_build['tasks_stats'] = \
                    self.stats_module_build_components(module_build)

            yield module_builds

            all_builds_finish = all((item['state_name'] in ('ready', 'failed')
                                     or (item['state_name'] == 'done'
                                         and item.get('scratch', False)))
                                    for item in module_builds)
            if all_builds_finish:
                break

            time.sleep(5)

    def module_watch_build(self, build_ids):
        """
        Watches the first MBS build in the list in a loop that updates every 15
        seconds. The loop ends when the build state is 'failed', 'done', or
        'ready'.

        :param build_ids: a list of module build IDs
        :type build_ids: list[int]
        """
        # Saved watched module builds got last time
        # build_id => module build dict
        last_builds = {}
        # Load anonymous Koji session in order to access the Koji web URL
        self.load_kojisession(anon=True)
        p = print

        def p_tasks(task_infos, task_state, head_line):
            p('    {0}:'.format(head_line))
            for ti in task_infos[task_state]:
                if ti['nvr'] is None:
                    # In some Koji task state, e.g. building state, no NVR is
                    # recorded in MBS.
                    p('      - %(package_name)s' % ti)
                else:
                    p('      - %(nvr)s' % ti)
                p('        {kojiweburl}/taskinfo?taskID={task_id}'.format(
                    kojiweburl=self.kojiweburl.rstrip('/'),
                    task_id=ti['task_id']
                ))

        def p_build_info_lines(build_info):
            p('[Build #%(id)s] %(name)s-%(stream)s-%(version)s-%(context)s '
              'is in "%(state_name)s" state.' % build_info)
            if build_info['id'] not in last_builds:
                p('  Koji tag: %(koji_tag)s' % build_info)
                p('  Link: %(link)s' % build_info)

        for module_builds in self.get_watched_module_builds(build_ids):
            for module_build in module_builds:
                module_build_id = module_build['id']
                state_name = module_build['state_name']

                # If module build state is not changed since last time, skip it
                # this time.
                # However, whether to handle state build will be delayed to
                # below by checking tasks statistics, since even if module
                # build is still in state build, task infos might changed, e.g.
                # some completed already or failed and new task started.
                if (state_name != 'build' and
                        last_builds.get(module_build_id, {})
                                   .get('state_name') == state_name):
                    continue

                # It's ok to get None, init state is the only one that does not
                # use tasks statistics and has no tasks for calculating statistics.
                stats = module_build.get('tasks_stats')

                if state_name == 'init':
                    p_build_info_lines(module_build)
                elif state_name == 'wait':
                    p_build_info_lines(module_build)
                    p('  Components: %(total)s' % stats)
                elif state_name in ('done', 'ready'):
                    p_build_info_lines(module_build)
                    p('  Components: %(done)s done, %(failed)s failed' % stats)
                elif state_name == 'failed':
                    p_build_info_lines(module_build)
                    p('  Components: %(done)s done, %(failed)s failed' % stats)
                    p('  Reason: %(state_reason)s' % module_build)
                elif state_name == 'build':
                    if module_build['id'] not in last_builds:
                        tasks_changed = True
                    else:
                        last_stats = last_builds[module_build['id']]['tasks_stats']
                        tasks_changed = (
                            stats['building'] != last_stats['building'] or
                            stats['failed'] > last_stats['failed']
                        )

                    if tasks_changed:
                        p_build_info_lines(module_build)
                        p('  Components: [%(completion_percentage)s%%]: %(building)s in building,'
                          ' %(done)s done, %(failed)s failed' % stats)

                        task_infos = module_build['tasks']['rpms']
                        if stats['building']:
                            p_tasks(task_infos, koji.BUILD_STATES['BUILDING'], 'Building')
                        else:
                            # This is a defense. When test watch with a real
                            # module build, a special case happens, that is all
                            # components build finished, but the module build
                            # got by watch command could be still in build state
                            # rather than the next state.
                            p('    No building task.')
                        if stats['failed']:
                            p_tasks(task_infos, koji.BUILD_STATES['FAILED'], 'Failed')

                last_builds[module_build_id] = module_build

    def module_get_api_version(self, api_url):
        """
        Queries the /about/ API to determine what the latest API version that
        MBS supports is and returns the latest API that both rpkg and MBS
        support.
        :param api_url: a string of the URL of the MBS API
        :return: an int of the API version
        """

        # We don't use self.module_api_url since this is used exclusively by the code
        # that is loading and validating the API URL before setting it.

        url = '{0}/about/'.format(api_url.rstrip('/'))
        response = requests.get(url, timeout=60)
        if response.ok:
            api_version = response.json().get('api_version', 1)
            if api_version >= 2:
                # Max out at API v2
                return 2
            else:
                return 1
        else:
            try:
                error_msg = response.json()['message']
            except (ValueError, KeyError):
                error_msg = response.text
            raise rpkgError(
                'The following error occurred while trying to determine the '
                'API versions supported by MBS: {0}'.format(error_msg))

    def remote(self, remote_name, repo_name):
        """Add remote pointing repository from remote dist-git service

        Simply a wrapper on 'git remote ...' interface that uses
        internal values to get package-specific target URL.

        :param str remote_name: chosen name for remote
        :param str repo_name: remote repository name. If remote repository has \
        same name as current repository, repo_name can be None
        """

        # gets the dist-git url for the project in the current folder.
        anongiturl = self._get_namespace_anongiturl(repo_name or self.ns_repo_name)

        ret, _, _ = self._run_command(['git', 'remote', 'add', remote_name, anongiturl])
        if ret == 0:
            self.log.info("Remote '{}' for '{}' was added.".format(remote_name, anongiturl))
        self._run_command(['git', 'fetch', remote_name])

    def load_nameverrel_dockerfile(self):

        named_version_pattern = re.compile(r"{0}_VERSION\s?=\s?([0-9.]+)".format(self.repo_name),
                                           re.IGNORECASE)
        version_pattern = re.compile(r"\bVERSION\b\s?=\s?([0-9.]+)", re.IGNORECASE)
        release_pattern = re.compile(r"\bRELEASE\b\s?=\s?([0-9.]+)", re.IGNORECASE)

        with open(os.path.join(self.layout.root_dir, "Dockerfile"), "r") as f:
            text = str(f.read())

            named_version_match = re.search(named_version_pattern, text)
            version_match = re.search(version_pattern, text)
            release_match = re.search(release_pattern, text)

            if named_version_match:
                version = named_version_match.group(1)
            else:
                if version_match:
                    version = version_match.group(1)
                else:
                    raise rpkgError('Could not query n-v-r of %s: no version in Dockerfile.'
                                    % (self.repo_name))

            if release_match:
                release = release_match.group(1)
            else:
                raise rpkgError('Could not query n-v-r of %s: no release value in Dockerfile.'
                                % (self.repo_name))

        return self._repo_name, version, release
