# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from hgitaly.tests.common import make_empty_repo

from hgitaly.stub.mercurial_repository_pb2 import (
    ConfigItemType,
    GetConfigItemRequest,
)
from hgitaly.stub.mercurial_repository_pb2_grpc import (
    MercurialRepositoryServiceStub,
)


def test_config_item(grpc_channel, server_repos_root):
    hg_repo_stub = MercurialRepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def rpc_config_bool(section, name):
        return hg_repo_stub.GetConfigItem(
            GetConfigItemRequest(repository=grpc_repo,
                                 section=section,
                                 name=name,
                                 as_type=ConfigItemType.BOOL)
        ).as_bool

    # Relying on current defaults in some random core settings, just pick
    # some other ones if they change.
    assert rpc_config_bool('format', 'usestore') is True
    assert rpc_config_bool('commands', 'status.verbose') is False
