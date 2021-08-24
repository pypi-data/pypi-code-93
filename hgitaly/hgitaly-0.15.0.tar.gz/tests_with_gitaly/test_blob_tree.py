# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest
import grpc


from hgitaly.oid import (
    blob_oid,
)
from hgitaly.stream import WRITE_BUFFER_SIZE

from hgitaly.stub.blob_pb2 import (
    GetBlobRequest,
    GetBlobsRequest,
)
from hgitaly.stub.commit_pb2 import (
    GetTreeEntriesRequest,
    TreeEntryRequest,
)
from hgitaly.stub.blob_pb2_grpc import BlobServiceStub
from hgitaly.stub.commit_pb2_grpc import CommitServiceStub

from . import skip_comparison_tests
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip


class TreeBlobFixture:

    def __init__(self, gitaly_comparison):
        self.comparison = gitaly_comparison
        self.hg_repo_wrapper = gitaly_comparison.hg_repo_wrapper
        self.git_repo = gitaly_comparison.git_repo

        self.gitaly_repo = gitaly_comparison.gitaly_repo
        self.commit_stubs = dict(
            git=CommitServiceStub(self.comparison.gitaly_channel),
            hg=CommitServiceStub(self.comparison.hgitaly_channel))
        self.blob_stubs = dict(
            git=BlobServiceStub(self.comparison.gitaly_channel),
            hg=BlobServiceStub(self.comparison.hgitaly_channel))

    def tree_entry(self, vcs, path, revision=b'branch/default',
                   limit=0, max_size=0):
        request = TreeEntryRequest(repository=self.gitaly_repo,
                                   revision=revision,
                                   limit=limit,
                                   max_size=max_size,
                                   path=path)
        resp = self.commit_stubs[vcs].TreeEntry(request)
        return [r for r in resp]

    def assert_compare_tree_entry(self, path, several_responses=False, **kw):
        hg_entries = self.tree_entry('hg', path, **kw)
        git_entries = self.tree_entry('hg', path, **kw)

        for entries in (hg_entries, git_entries):
            for r in entries:
                # oid should be the only difference in comparison
                r.oid = ''

        assert hg_entries == git_entries
        if several_responses:
            assert len(hg_entries) > 1

    def assert_error_compare_tree_entry(self, path, **kw):
        with pytest.raises(grpc.RpcError) as hg_err_info:
            self.tree_entry('hg', path, **kw)
        with pytest.raises(grpc.RpcError) as git_err_info:
            self.tree_entry('git', path, **kw)

        assert hg_err_info.value.code() == git_err_info.value.code()
        assert hg_err_info.value.details() == git_err_info.value.details()

    def get_blob(self, vcs, oid, limit=-1):
        request = GetBlobRequest(repository=self.gitaly_repo,
                                 limit=limit,
                                 oid=oid)

        return [r for r in self.blob_stubs[vcs].GetBlob(request)]

    def get_blobs(self, vcs, rev_paths, limit=-1, **request_kw):
        rev_path_msgs = [
            GetBlobsRequest.RevisionPath(revision=rev, path=path)
            for rev, path in rev_paths
        ]
        request = GetBlobsRequest(repository=self.gitaly_repo,
                                  revision_paths=rev_path_msgs,
                                  limit=limit,
                                  **request_kw)

        return [r for r in self.blob_stubs[vcs].GetBlobs(request)]

    def get_tree_entries(self, vcs, path, revision=b'branch/default',
                         recursive=False):
        request = GetTreeEntriesRequest(repository=self.gitaly_repo,
                                        revision=revision,
                                        recursive=recursive,
                                        path=path)

        resp = self.commit_stubs[vcs].GetTreeEntries(request)
        # let's hope ordering doesn't matter
        return {entry.path: entry
                for chunk in resp for entry in chunk.entries}

    def assert_compare_get_tree_entries(self, path, **kw):
        hg_tree_entries = self.get_tree_entries('hg', path, **kw)
        git_tree_entries = self.get_tree_entries('git', path, **kw)

        # TODO itertools
        for entry in (v for d in (git_tree_entries, hg_tree_entries)
                      for v in d.values()):
            entry.oid = entry.root_oid = ''

        assert hg_tree_entries == git_tree_entries


@pytest.fixture
def tree_blob_fixture(gitaly_comparison):
    yield TreeBlobFixture(gitaly_comparison)


def test_compare_tree_entry_request(tree_blob_fixture):
    fixture = tree_blob_fixture

    wrapper = fixture.hg_repo_wrapper
    wrapper.write_commit('foo', message="Some foo")
    sub = (wrapper.path / 'sub')
    sub.mkdir()
    (sub / 'bar').write_text('bar content')
    (sub / 'ba2').write_text('ba2 content')
    # TODO OS indep for paths (actually TODO make wrapper.commit easier to
    # use, e.g., check how to make it accept patterns)
    wrapper.commit(rel_paths=['sub/bar', 'sub/ba2'],
                   message="zebar", add_remove=True)

    # precondition for the test: mirror worked
    assert fixture.git_repo.branch_titles() == {b'branch/default': b"zebar"}

    for path in (b'sub', b'sub/bar', b'sub/', b'.', b'do-not-exist'):
        fixture.assert_compare_tree_entry(path)

    # limit and max_size (does not apply to Trees)
    fixture.assert_compare_tree_entry(b'foo', limit=4)
    fixture.assert_error_compare_tree_entry(b'foo', max_size=4)
    fixture.assert_compare_tree_entry(b'sub', max_size=1)

    # unknown revision (not an error)
    fixture.assert_compare_tree_entry(b'sub', revision=b'unknown')

    # chunking for big Blob entry
    wrapper.write_commit('bigfile', message="A big file",
                         content=b"big" + b'ff' * WRITE_BUFFER_SIZE)
    fixture.assert_compare_tree_entry(b'bigfile', several_responses=True)

    # reusing content to test GetTreeEntries
    for path in (b'.', b'sub'):
        for recursive in (False, True):
            fixture.assert_compare_get_tree_entries(path, recursive=recursive)


def test_compare_get_blob_request(tree_blob_fixture):
    fixture = tree_blob_fixture
    git_repo = fixture.git_repo

    wrapper = fixture.hg_repo_wrapper
    large_data = b'\xbe' * WRITE_BUFFER_SIZE + b'\xefdata'

    wrapper.commit_file('small', message="Small file")
    changeset = wrapper.commit_file('foo', message="Large foo",
                                    content=large_data)

    # mirror worked
    assert git_repo.branch_titles() == {b'branch/default': b"Large foo"}

    oids = dict(
        git=fixture.tree_entry('git', b'foo', limit=1)[0].oid,
        hg=blob_oid(wrapper.repo, changeset.hex().decode(), b'foo')
    )

    git_resps = fixture.get_blob('git', oids['git'], limit=12)
    # important assumption for hg implementation:
    assert git_resps[0].oid == oids['git']

    hg_resps = fixture.get_blob('hg', oids['hg'], limit=12)
    assert len(hg_resps) == 1  # double-check: already done in direct hg test
    assert len(git_resps) == 1
    git_resp, hg_resp = git_resps[0], hg_resps[0]
    assert hg_resp.size == git_resp.size
    assert hg_resp.data == git_resp.data

    git_resps = fixture.get_blob('git', oids['git'])

    hg_resps = fixture.get_blob('hg', oids['hg'])
    # Gitaly chunking is not fully deterministic, so the most
    # we can check is that chunking occurs for both servers
    # and that the first and second responses have the same metadata
    assert len(hg_resps) > 1
    assert len(git_resps) > 1

    assert hg_resps[0].oid == oids['hg']
    assert git_resps[0].oid == oids['git']
    assert hg_resps[1].oid == git_resps[1].oid
    for hgr, gitr in zip(hg_resps[:2], git_resps[:2]):
        assert hgr.size == gitr.size

    assert (
        b''.join(r.data for r in hg_resps)
        ==
        b''.join(r.data for r in git_resps)
    )

    # now with get_blobs
    rev_paths = ((b'branch/default', b'small'),
                 (b'branch/default', b'does-not-exist'),
                 (b'no-such-revision', b'small'),
                 )

    hg_resps = fixture.get_blobs('hg', rev_paths)
    git_resps = fixture.get_blobs('git', rev_paths)

    for resp in hg_resps:
        resp.oid = ''
    for resp in git_resps:
        resp.oid = ''

    assert hg_resps == git_resps

    # with limits (the limit is per file)
    hg_resps = fixture.get_blobs('hg', rev_paths, limit=3)
    git_resps = fixture.get_blobs('git', rev_paths, limit=3)

    for resp in hg_resps:
        resp.oid = ''
    for resp in git_resps:
        resp.oid = ''

    assert hg_resps == git_resps

    # chunking in get_blobs, again non-deterministic for Gitaly
    rev_paths = ((b'branch/default', b'small'),
                 (b'branch/default', b'foo'),
                 )
    hg_resps = fixture.get_blobs('hg', rev_paths)
    git_resps = fixture.get_blobs('git', rev_paths)
    assert len(hg_resps) > 2
    assert len(git_resps) > 2
    assert hg_resps[0].oid != ""
    assert git_resps[0].oid != ""
    assert hg_resps[1].oid != ""
    assert git_resps[1].oid != ""
    assert hg_resps[2].oid == ""
    assert git_resps[2].oid == ""
    for hgr, gitr in zip(hg_resps[:3], git_resps[:3]):
        assert hgr.size == gitr.size

    assert (  # content of the big file at 'foo'
        b''.join(r.data for r in hg_resps[1:])
        ==
        b''.join(r.data for r in git_resps[1:])
    )
