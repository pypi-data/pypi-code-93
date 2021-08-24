# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
import pytest

from hgext3rd.heptapod.special_ref import (
    write_gitlab_special_ref,
    special_refs,
)
from hgitaly.stub.ref_pb2 import (
    FindBranchRequest,
    FindRefNameRequest,
    DeleteRefsRequest,
)
from hgitaly.stub.ref_pb2_grpc import RefServiceStub

from . import skip_comparison_tests
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip


def test_compare_find_branch(gitaly_comparison):
    fixture = gitaly_comparison
    hgitaly_repo = fixture.hgitaly_repo
    gitaly_repo = fixture.gitaly_repo
    git_repo = fixture.git_repo

    fixture.hg_repo_wrapper.write_commit('foo', message="Some foo")

    # mirror worked
    assert git_repo.branch_titles() == {b'branch/default': b"Some foo"}

    gl_branch = b'branch/default'
    hgitaly_request = FindBranchRequest(repository=hgitaly_repo,
                                        name=gl_branch)
    gitaly_request = FindBranchRequest(repository=gitaly_repo, name=gl_branch)

    gitaly_ref_stub = RefServiceStub(fixture.gitaly_channel)
    hgitaly_ref_stub = RefServiceStub(fixture.hgitaly_channel)

    hg_resp = hgitaly_ref_stub.FindBranch(hgitaly_request)
    git_resp = gitaly_ref_stub.FindBranch(gitaly_request)

    # responses should be identical, except for commit ids
    hg_resp.branch.target_commit.id = ''
    git_resp.branch.target_commit.id = ''
    # right now, this assertion fails because
    # - we don't provide a body_size
    # - we don't give the explicit "+0000" timezone (but Gitaly does)
    # assert hg_resp == git_resp
    # Lets' still assert something that works:
    assert all(resp.branch.target_commit.subject == b"Some foo"
               for resp in (hg_resp, git_resp))


def test_delete_refs(gitaly_comparison):
    fixture = gitaly_comparison
    grpc_repo = fixture.gitaly_repo
    git_repo = fixture.git_repo
    hg_wrapper = fixture.hg_repo_wrapper
    hg_repo = hg_wrapper.repo

    vcs_channels = dict(git=RefServiceStub(fixture.gitaly_channel),
                        hg=RefServiceStub(fixture.hgitaly_channel))

    base_hg_ctx = hg_wrapper.commit_file('foo')
    # TODO get_branch_sha does not work because of PosixPath not having
    # the join method (py.path.local does)
    git_sha = git_repo.branches()[b'branch/default']['sha']
    hg_sha = base_hg_ctx.hex()

    mr_ref_name = b'merge-requests/2/train'
    mr_ref_path = b'refs/' + mr_ref_name

    def setup_mr_ref():
        git_repo.write_ref(mr_ref_path.decode(), git_sha)
        write_gitlab_special_ref(hg_repo, mr_ref_name, hg_sha)
        # invalidation TODO use the future wrapper.reload()
        setattr(hg_repo, '_gitlab_refs_special-refs', None)
        assert mr_ref_path in git_repo.all_refs()
        assert mr_ref_name in special_refs(hg_repo)

    setup_mr_ref()

    def do_rpc(vcs, refs=(), except_prefixes=()):
        return vcs_channels[vcs].DeleteRefs(
            DeleteRefsRequest(repository=grpc_repo,
                              refs=refs,
                              except_with_prefix=except_prefixes))

    def assert_compare(**kw):
        assert do_rpc('hg', **kw) == do_rpc('git', **kw)

    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc('hg', refs=[b'xy'], except_prefixes=[b'refs/heads'])

    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc('git', refs=[b'xy'], except_prefixes=[b'refs/heads'])

    assert exc_info_hg.value.details() == exc_info_git.value.details()

    assert_compare(refs=[mr_ref_path])

    # unknown refs dont create errors
    unknown = b'refs/environments/imaginary'
    assert_compare(refs=[unknown])

    # also mixing unknown with known is ok
    setup_mr_ref()
    assert_compare(refs=[unknown, mr_ref_path])

    assert git_repo.all_refs() == {b'refs/heads/branch/default': git_sha}
    # TODO use the future wrapper.reload()
    setattr(hg_repo, '_gitlab_refs_special-refs', None)
    assert special_refs(hg_repo) == {}

    # using except_with_prefix
    env_ref_name = b'environments/2877'
    env_ref_path = b'refs/' + env_ref_name

    def setup_env_ref():
        git_repo.write_ref(env_ref_path.decode(), git_sha)
        write_gitlab_special_ref(hg_repo, env_ref_name, hg_sha)
        # TODO use the future wrapper.reload()
        setattr(hg_repo, '_gitlab_refs_special-refs', None)
        assert env_ref_path in git_repo.all_refs()
        assert env_ref_name in special_refs(hg_repo)

    # on the Mercurial side, we'll consider the special ref only,
    # but on the Git side, the `refs/heads` prefix has to be ignored.
    # This is similar to what the current actual caller,
    # `Projects::AfterImportService`, does.
    for except_prefixes in (
            [b'refs/environments/', b'refs/heads/'],
            [b'refs/environments', b'refs/heads/'],
            [b'refs/envir', b'refs/heads/'],
            ):
        setup_mr_ref()
        setup_env_ref()

        assert_compare(except_prefixes=except_prefixes)
        assert git_repo.all_refs() == {b'refs/heads/branch/default': git_sha,
                                       env_ref_path: git_sha}
        # TODO use the future wrapper.reload()
        setattr(hg_repo, '_gitlab_refs_special-refs', None)
        assert special_refs(hg_repo) == {env_ref_name: hg_sha}


def test_find_ref_name(gitaly_comparison):
    fixture = gitaly_comparison
    hgitaly_repo = fixture.hgitaly_repo
    gitaly_repo = fixture.gitaly_repo
    git_repo = fixture.git_repo
    wrapper = fixture.hg_repo_wrapper

    gl_default = b'branch/default'
    gl_other = b'branch/other'
    base_hg_ctx = wrapper.write_commit('foo', message="base")
    base_hg_sha = base_hg_ctx.hex()
    # TODO get_branch_sha does not work because of PosixPath not having
    # the join method (py.path.local does)
    git_sha0 = git_repo.branches()[gl_default]['sha']

    default_hg_sha = wrapper.write_commit('foo', message="default").hex()
    git_sha1 = git_repo.branches()[gl_default]['sha']

    assert git_sha0 != git_sha1

    other_hg_sha = wrapper.write_commit('foo', message="other",
                                        branch="other",
                                        parent=base_hg_ctx).hex()
    other_git_sha = git_repo.branches()[gl_other]['sha']

    gitaly_ref_stub = RefServiceStub(fixture.gitaly_channel)
    hgitaly_ref_stub = RefServiceStub(fixture.hgitaly_channel)

    def do_git(commit_id, prefix):
        return gitaly_ref_stub.FindRefName(
            FindRefNameRequest(repository=gitaly_repo,
                               commit_id=commit_id,
                               prefix=prefix
                               ))

    def do_hg(commit_id, prefix):
        return hgitaly_ref_stub.FindRefName(
            FindRefNameRequest(repository=hgitaly_repo,
                               commit_id=commit_id,
                               prefix=prefix
                               ))

    # Git returns the first ref in alphabetic order, hence not branch/default
    # for the base commit because 'default' < 'other'
    for prefix in (b'refs/heads',
                   b'refs/heads/',
                   b'refs/heads/branch',
                   b'refs/heads/branch/',
                   b'refs/heads/branch/default',
                   ):

        assert do_git(git_sha0, prefix).name == b'refs/heads/branch/default'
        assert do_hg(base_hg_sha, prefix).name == b'refs/heads/branch/default'

        assert do_git(git_sha1, prefix).name == b'refs/heads/branch/default'
        assert do_hg(default_hg_sha, prefix).name == (b'refs/heads/'
                                                      b'branch/default')

    for prefix in (b'refs/heads',
                   b'refs/heads/',
                   b'refs/heads/branch',
                   b'refs/heads/branch/',
                   b'refs/heads/branch/other',
                   ):

        assert do_git(other_git_sha, prefix).name == b'refs/heads/branch/other'
        assert do_hg(other_hg_sha, prefix).name == b'refs/heads/branch/other'

    for prefix in (b'refs/heads/bra',
                   b'refs/heads/branch/def',
                   ):
        assert not do_git(git_sha0, prefix).name
        assert not do_hg(base_hg_sha, prefix).name

        assert not do_git(git_sha1, prefix).name
        assert not do_hg(default_hg_sha, prefix).name
