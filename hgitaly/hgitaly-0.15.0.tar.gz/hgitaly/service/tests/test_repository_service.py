# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from contextlib import contextmanager
from io import BytesIO
import grpc
import shutil
import tarfile
from mercurial_testhelpers.util import as_bytes

import pytest

from hgext3rd.heptapod.branch import read_gitlab_typed_refs
from hgext3rd.heptapod.keep_around import (
    create_keep_around,
    iter_keep_arounds,
)

from hgitaly.tests.common import make_empty_repo
from hgitaly.stub.shared_pb2 import Repository

from hgitaly.stub.repository_service_pb2 import (
    CreateRepositoryRequest,
    FindMergeBaseRequest,
    GetArchiveRequest,
    HasLocalBranchesRequest,
    RepositoryExistsRequest,
    WriteRefRequest,
)
from hgitaly.stub.repository_service_pb2_grpc import RepositoryServiceStub
from mercurial import (
    error,
    hg,
    node as node_mod,
    pycompat,
)
from heptapod.testhelpers import (
    make_ui,
    LocalRepoWrapper,
)


def test_repository_exists(grpc_channel, server_repos_root):
    repo_stub = RepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def exists(repo):
        return repo_stub.RepositoryExists(
            RepositoryExistsRequest(repository=repo)).exists

    assert exists(grpc_repo)

    # directory exists but is not a Mercurial repo
    shutil.rmtree(wrapper.path / '.hg')
    assert not exists(grpc_repo)

    # directory does not exist
    grpc_repo.relative_path = 'does/not/exist'
    assert not exists(grpc_repo)


def test_has_local_branches(grpc_channel, server_repos_root):
    repo_stub = RepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def has_local_branches():
        return repo_stub.HasLocalBranches(
            HasLocalBranchesRequest(repository=grpc_repo)).value

    assert not has_local_branches()
    wrapper.write_commit('foo')
    assert has_local_branches()

    wrapper.command('commit', message=b"closing the only head!",
                    close_branch=True)

    assert not has_local_branches()


def test_write_ref(grpc_channel, server_repos_root):
    repo_stub = RepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    repo = wrapper.repo

    for ref, revision in ((b'refs/heads/something', b'dead01234cafe'),
                          (b'HEAD', b'topic/default/wont-last'),
                          (b'refs/keep-around/not-a-sha', b'not-a-sha'),
                          (b'refs/keep-around/feca01eade', b'cafe01dead'),
                          ):
        with pytest.raises(grpc.RpcError) as exc_info:
            repo_stub.WriteRef(WriteRefRequest(
                repository=grpc_repo,
                ref=ref,
                revision=revision
            ))
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    changeset = wrapper.commit_file('foo')

    to_write = {b'refs/merge-requests/12/head': changeset.hex(),
                b'refs/pipelines/98192': b'refs/heads/branch/default',
                b'refs/environments/13/deployments/9826': b'branch/default',
                }
    for ref_path, target in to_write.items():
        repo_stub.WriteRef(WriteRefRequest(
            repository=grpc_repo,
            ref=ref_path,
            revision=target))

    # read without any caching
    assert read_gitlab_typed_refs(wrapper.repo, 'special-refs') == {
        ref_path[5:]: changeset.hex() for ref_path in to_write.keys()
    }

    # Keep-arounds. let's have a pre-existing one for good measure
    existing_ka = b'c8c3ae298f5549a0eb0c28225dcc4f6937b959a8'
    create_keep_around(repo, existing_ka)

    repo_stub.WriteRef(WriteRefRequest(
        repository=grpc_repo,
        ref=b'refs/keep-around/' + changeset.hex(),
        revision=changeset.hex()))

    assert set(iter_keep_arounds(repo)) == {changeset.hex(), existing_ka}


def test_write_special_refs_exceptions(
        grpc_channel, server_repos_root, monkeypatch):
    repo_stub = RepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    wrapper.commit_file('foo')

    (wrapper.path / '.hg' / 'store' / 'gitlab.special-refs').write_text(
        'invalid')

    repo_stub.WriteRef(WriteRefRequest(
        repository=grpc_repo,
        ref=b'refs/merge-requests/12/head',
        revision=b'76ac23fe' * 5))


@contextmanager
def get_archive_tarfile(stub, grpc_repo, commit_id, path=b''):
    with BytesIO() as fobj:
        for chunk_index, chunk_response in enumerate(
                stub.GetArchive(GetArchiveRequest(
                    repository=grpc_repo,
                    format=GetArchiveRequest.Format.Value('TAR'),
                    commit_id=commit_id,
                    path=path,
                    prefix='archive-dir',
                ))):
            fobj.write(chunk_response.data)

        fobj.seek(0)
        with tarfile.open(fileobj=fobj) as tarf:
            yield tarf, chunk_index + 1


def test_get_archive(grpc_channel, server_repos_root, tmpdir):
    repo_stub = RepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    ctx = wrapper.write_commit('foo', content="Foo")
    (wrapper.path / 'sub').mkdir()
    ctx2 = wrapper.write_commit('sub/bar', content="Bar")

    node_str = ctx.hex().decode()
    with get_archive_tarfile(repo_stub, grpc_repo, node_str) as (tarf, _nb):
        assert set(tarf.getnames()) == {'archive-dir/.hg_archival.txt',
                                        'archive-dir/foo'}

        extract_dir = tmpdir.join('extract')
        tarf.extractall(path=extract_dir)

        metadata_lines = extract_dir.join('archive-dir',
                                          '.hg_archival.txt').readlines()

        assert 'node: %s\n' % node_str in metadata_lines
        assert extract_dir.join('archive-dir', 'foo').read() == "Foo"

    node2_str = ctx2.hex().decode()
    with get_archive_tarfile(repo_stub, grpc_repo, node2_str) as (tarf, _nb):
        assert set(tarf.getnames()) == {'archive-dir/.hg_archival.txt',
                                        'archive-dir/foo',
                                        'archive-dir/sub/bar'}

        extract_dir = tmpdir.join('extract-2')
        tarf.extractall(path=extract_dir)

        metadata_lines = extract_dir.join('archive-dir',
                                          '.hg_archival.txt').readlines()

        assert 'node: %s\n' % node2_str in metadata_lines
        assert extract_dir.join('archive-dir', 'sub', 'bar').read() == "Bar"

    with get_archive_tarfile(
            repo_stub, grpc_repo, node2_str, path=b'sub') as (tarf, _nb):
        assert tarf.getnames() == ['archive-dir/sub/bar']

        extract_dir = tmpdir.join('extract-sub')
        tarf.extractall(path=extract_dir)
        assert extract_dir.join('archive-dir', 'sub', 'bar').read() == "Bar"

    with pytest.raises(grpc.RpcError) as exc_info:
        get_archive_tarfile(
            repo_stub, grpc_repo, node2_str,
            path=b'/etc/passwd'
        ).__enter__()  # needed to actually perform the RPC call
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT


def test_get_archive_multiple_chunks(grpc_channel, server_repos_root,
                                     tmpdir, monkeypatch):

    repo_stub = RepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    # we can't just override the environment variable: it's read at module
    # import time.
    large_content = "Foo" * 200000
    ctx = wrapper.write_commit('foo', content=large_content)
    node_str = ctx.hex().decode()
    with get_archive_tarfile(repo_stub, grpc_repo, node_str) as (tarf, count):
        assert count > 1
        assert set(tarf.getnames()) == {'archive-dir/.hg_archival.txt',
                                        'archive-dir/foo'}

        extract_dir = tmpdir.join('extract')
        tarf.extractall(path=extract_dir)

        metadata_lines = extract_dir.join('archive-dir',
                                          '.hg_archival.txt').readlines()

        assert 'node: %s\n' % node_str in metadata_lines
        assert extract_dir.join('archive-dir', 'foo').read() == large_content

    del large_content


def test_find_merge_base(grpc_channel, server_repos_root):
    repo_stub = RepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    # repo structure:
    #
    #   o 2 add animal (branch/stable)
    #   |
    #   | 1 add bar
    #   |/
    #   |
    #   o 0 add foo
    #
    ctx0 = wrapper.write_commit('foo')
    sha0 = ctx0.hex()
    sha1 = wrapper.write_commit('bar').hex()
    sha2 = wrapper.write_commit('animal', branch='stable', parent=ctx0).hex()
    # commting new root, to test no gca case
    sha3 = wrapper.commit_file('tut', branch='other',
                               parent=node_mod.nullid).hex()

    def do_rpc(revisions):
        request = FindMergeBaseRequest(
            repository=grpc_repo,
            revisions=revisions,
        )
        response = repo_stub.FindMergeBase(request)
        return pycompat.sysbytes(response.base)

    # Actual test
    assert do_rpc([sha1, sha2]) == sha0
    assert do_rpc([b'branch/stable', sha1]) == sha0

    # when no merge base (gca) found
    assert do_rpc([sha0, sha3]) == b''

    # test with invalid_argument, as it requires minimum 2 revisions
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc([sha0])
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert (
        exc_info.value.details()
        ==
        'FindMergeBase: at least 2 revisions are required'
    )

    sha_not_exists = b'deadnode' * 5
    assert do_rpc([sha0, sha_not_exists]) == b''


def test_create_repository(grpc_channel, server_repos_root):
    rel_path = 'sample_repo'
    default_storage = 'default'
    repo_stub = RepositoryServiceStub(grpc_channel)
    ui = make_ui(None)
    path = server_repos_root / default_storage / rel_path
    pathb = as_bytes(path)

    # try to instantiate wrapper before repo creation
    with pytest.raises(error.RepoError) as exc_info:
        LocalRepoWrapper(hg.repository(ui, pathb), path)
    assert b''.join(exc_info.value.args).endswith(b'sample_repo not found')

    def do_rpc(rel_path, storage=default_storage):
        grpc_repo = Repository(relative_path=rel_path, storage_name=storage)
        request = CreateRepositoryRequest(repository=grpc_repo)
        response = repo_stub.CreateRepository(request)
        return response

    do_rpc(rel_path)
    # instantiating wrapper to check successful repo creation
    wrapper = LocalRepoWrapper(hg.repository(ui, pathb), path)
    assert wrapper.repo.path.endswith(b'default/sample_repo/.hg')

    # To follow along with Gitaly, attempt to create existing repo
    # shouldn't respond with any error
    do_rpc(rel_path)

    # when storage name doesn't exists
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(rel_path, storage='cargoship')
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert 'no such storage' in exc_info.value.details()

    # test with a broken symlink (which points to itself)
    brepo_name = "myrepo_a_broken_symlink"
    path = (server_repos_root / default_storage / brepo_name)
    path.symlink_to(path)
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(brepo_name)
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'Too many levels of symbolic links' in exc_info.value.details()
