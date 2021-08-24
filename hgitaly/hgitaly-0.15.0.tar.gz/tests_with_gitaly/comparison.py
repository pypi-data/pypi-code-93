# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixture for Gitaly comparison tests based on Heptapod's Git mirroring."""
import attr
import contextlib
import random

from heptapod.testhelpers.gitlab import GitLabMirrorFixture
from hgitaly.stub.shared_pb2 import Repository


@attr.s
class GitalyComparison:
    hgitaly_channel = attr.ib()
    gitaly_channel = attr.ib()
    gitaly_repo = attr.ib()
    hgitaly_repo = attr.ib()
    gitlab_mirror = attr.ib()

    @property
    def hg_repo_wrapper(self):
        return self.gitlab_mirror.hg_repo_wrapper

    @property
    def git_repo(self):
        return self.gitlab_mirror.git_repo


@contextlib.contextmanager
def gitaly_comparison_fixture(server_repos_root,
                              gitaly_channel,
                              grpc_channel,
                              monkeypatch,
                              ):
    common_relative_path = 'repo-' + hex(random.getrandbits(64))[2:]
    storage = 'default'

    gitaly_repo = Repository(relative_path=common_relative_path + '.git',
                             storage_name=storage)
    hgitaly_repo = Repository(relative_path=common_relative_path + '.hg',
                              storage_name=storage)

    hg_config = dict(phases=dict(publish=False),
                     extensions={name: '' for name in ('evolve',
                                                       'hggit',
                                                       'topic',
                                                       'heptapod')})
    with GitLabMirrorFixture.init(
            server_repos_root / storage,
            monkeypatch,
            common_repo_name=common_relative_path,
            hg_config=hg_config,
    ) as mirror:
        # configuration must be written in HGRC file, because
        # HGitaly server will load the repository independently.
        mirror.hg_repo_wrapper.write_hgrc(hg_config)
        mirror.activate_mirror()
        yield GitalyComparison(
            hgitaly_channel=grpc_channel,
            hgitaly_repo=hgitaly_repo,
            gitaly_channel=gitaly_channel,
            gitaly_repo=gitaly_repo,
            gitlab_mirror=mirror,
        )
