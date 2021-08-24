# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from mercurial import (
    pycompat,
)
from heptapod.testhelpers import (
    LocalRepoWrapper,
)

from ..stub.shared_pb2 import (
    CommitAuthor,
    Repository,
    SignatureType,
)

from .. import message


def test_tag(tmpdir):
    wrapper = LocalRepoWrapper.init(tmpdir)
    repo = wrapper.repo

    ctx = wrapper.write_commit('foo', message="The tagged chgs")

    # the factory function doesn't even need the tag to actually exist
    tag = message.tag(b'v3.2.1', ctx)
    assert tag.name == b'v3.2.1'
    assert not tag.id
    assert not tag.message
    assert not tag.message_size
    assert tag.tagger == CommitAuthor()
    assert tag.signature_type == SignatureType.NONE

    # we'll need a real tagging changeset
    wrapper.command('tag', b'v3.2.1', rev=ctx.hex(),
                    message=b'Setting the tag',
                    )
    tagging_ctx = repo[b'.']

    tag = message.tag(b'v3.2.1', ctx,
                      tagging=tagging_ctx,
                      signature_type=SignatureType.PGP)

    assert tag.name == b'v3.2.1'
    assert pycompat.sysbytes(tag.id) == tagging_ctx.hex()
    assert tag.message == b'Setting the tag'
    assert tag.message_size == 15
    assert tag.tagger == message.commit_author(tagging_ctx)
    assert tag.signature_type == SignatureType.PGP


def test_logging_class():
    log_msg = message.Logging(Repository(storage_name='thestore',
                                         relative_path='a/b/c'))
    assert repr(log_msg) == (
        'Repository { storage_name: "thestore" relative_path: "a/b/c" }'
    )
