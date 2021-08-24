# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import attr
from contextlib import contextmanager
import grpc
import os
import subprocess

from hgitaly.stub.repository_service_pb2 import RepositoryExistsRequest
from hgitaly.stub.shared_pb2 import Repository
from hgitaly.stub.repository_service_pb2_grpc import RepositoryServiceStub

from . import GITALY_INSTALL_DIR


def wait_gitaly_accepts_connection(gitaly_channel, timeout=5):
    """Wait for the Gitaly server to accept connections.

    wait for server to start enough that the address in bound
    Then the `wait_for_ready` optionis there to ensure full readiness, but
    the client must at least receive something, e.g., the `CONNECTING` status
    for that to work.
    """
    repo_stub = RepositoryServiceStub(gitaly_channel)
    repo_stub.RepositoryExists(
        RepositoryExistsRequest(
            repository=Repository(
                relative_path="we/dont/care/waiting/for/any/connection",
                storage_name="default")
        ),
        timeout=timeout,
        wait_for_ready=True
    )


@attr.s
class GitalyServer:
    home_dir = attr.ib()

    def configure(self):
        home_dir = self.home_dir
        self.gitaly_conf = home_dir / 'gitaly_config.toml'
        self.gitaly_socket = home_dir / 'gitaly.socket'

        # this is required even if we won't use it (we're not sending any
        # GitLab hooks)
        gitlab_shell_dir = home_dir / 'gitlab-shell'
        gitlab_shell_dir.mkdir()

        default_storage = home_dir / 'default'
        default_storage.mkdir()
        self.gitaly_conf.write_text("\n".join((
            'socket_path = "%s"' % self.gitaly_socket,
            # Gitaly compilation outputs its binaries at the root
            # of the checkout
            'bin_dir = "%s"' % GITALY_INSTALL_DIR,
            '[gitlab-shell]',
            'dir = "%s"' % gitlab_shell_dir,
            '[gitaly-ruby]',
            'dir = "%s"' % (GITALY_INSTALL_DIR / 'ruby'),
            '[[storage]]',
            'name = "default"',
            'path = "%s"' % default_storage,
            ''
        )))

    @contextmanager
    def start(self):
        self.configure()

        env = dict(os.environ)
        env['GITALY_TESTING_NO_GIT_HOOKS'] = "1"
        timeout = int(env.pop('GITALY_STARTUP_TIMEOUT', '5').strip())

        # Note: Python 3.8 does not need the conversions to str, but it's
        # handy to support Python 3.7 (Debian buster in CI)
        gitaly = subprocess.Popen([str(GITALY_INSTALL_DIR / 'gitaly'),
                                   str(self.gitaly_conf)],
                                  env=env)

        with grpc.insecure_channel('unix:' + str(self.gitaly_socket),
                                   ) as gitaly_channel:
            wait_gitaly_accepts_connection(gitaly_channel, timeout=timeout)
            yield gitaly_channel

        gitaly.terminate()
        gitaly.wait()
