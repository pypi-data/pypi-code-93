# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
import pytest
from mercurial import (
    pycompat,
)
from hgext3rd.heptapod.special_ref import (
    special_refs,
    write_gitlab_special_ref,
)
from hgext3rd.heptapod.keep_around import (
    create_keep_around,
)
from hgitaly.tests.common import (
    make_empty_repo,
    make_tree_shaped_repo,
)

from hgitaly.stub.shared_pb2 import (
    Tag,
)
from hgitaly.stub.ref_pb2 import (
    FindAllBranchNamesRequest,
    FindRefNameRequest,
    FindAllTagNamesRequest,
    RefExistsRequest,
    FindBranchRequest,
    FindLocalBranchesRequest,
    FindAllRemoteBranchesRequest,
    FindAllBranchesRequest,
    DeleteRefsRequest,
    ListBranchNamesContainingCommitRequest,
    ListTagNamesContainingCommitRequest,
    GetTagMessagesRequest,
    PackRefsRequest,
    PackRefsResponse,
    FindTagRequest,
)
from hgitaly.stub.ref_pb2_grpc import RefServiceStub

from hgext3rd.heptapod.branch import (
    write_gitlab_branches,
)


def test_find_all_branch_names(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    default_ctx = wrapper.write_commit('foo')
    wrapper.write_commit('foo', branch='other')
    wrapper.write_commit('foo', parent=default_ctx, topic='zz-top')

    request = FindAllBranchNamesRequest(repository=grpc_repo)

    resp = ref_stub.FindAllBranchNames(request)
    assert [set(chunk.names) for chunk in resp] == [
        {b'refs/heads/branch/default',
         b'refs/heads/branch/other',
         b'refs/heads/topic/default/zz-top',
         }]


def test_find_all_branch_names_chunks(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    for i in range(22):
        wrapper.write_commit('foo', branch='br%d' % i, return_ctx=False)

    request = FindAllBranchNamesRequest(repository=grpc_repo)

    chunks = [chunk for chunk in ref_stub.FindAllBranchNames(request)]
    assert len(chunks) == 2

    assert len(chunks[0].names) == 20
    assert len(chunks[1].names) == 2
    assert set(name for chunk in chunks for name in chunk.names) == {
        b'refs/heads/branch/br%d' % i for i in range(22)}


def test_tags(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    ctx = wrapper.write_commit('foo', message="The tagged chgs")
    wrapper.command('tag', b'v3.2.1', rev=ctx.hex())

    request = FindAllTagNamesRequest(repository=grpc_repo)

    resp = ref_stub.FindAllTagNames(request)
    assert [chunk.names for chunk in resp] == [[b'refs/tags/v3.2.1']]

    tag = ref_stub.FindTag(FindTagRequest(repository=grpc_repo,
                                          tag_name=b'v3.2.1')).tag
    assert tag.name == b'v3.2.1'
    target = tag.target_commit
    assert target.subject == b"The tagged chgs"

    resp = ref_stub.FindAllTags(request)
    assert [list(chunk.tags) for chunk in resp] == [[tag]]

    # finally a non existing tag
    notfound = ref_stub.FindTag(FindTagRequest(repository=grpc_repo,
                                               tag_name=b'does-not-exist')).tag
    assert notfound == Tag()  # gRPC uses default values to mean None/null/nil


def test_find_branch(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    ctx = wrapper.write_commit('foo', message="Ze subject")
    resp = ref_stub.FindBranch(
        FindBranchRequest(repository=grpc_repo,
                          name=b'branch/default'))
    branch = resp.branch
    assert branch is not None
    assert branch.name == b'branch/default'
    assert branch.target_commit.id == ctx.hex().decode()

    resp = ref_stub.FindBranch(
        FindBranchRequest(repository=grpc_repo,
                          name=b'refs/heads/branch/default'))
    assert resp.branch == branch

    resp = ref_stub.FindBranch(
        FindBranchRequest(repository=grpc_repo,
                          name=b'cannot-be-found'))
    assert not resp.branch.name

    resp = ref_stub.FindBranch(
        FindBranchRequest(repository=grpc_repo,
                          name=b'refs/keeparound/012ca34fe56'))

    # There is no None in gRPC, just cascading default content (empty string).
    # We checked that Gitaly indeed uses the default `Branch(name=b'')`
    # to represent the absence of results.
    assert not resp.branch.name

    resp = ref_stub.FindLocalBranches(
        FindLocalBranchesRequest(repository=grpc_repo))
    branches = [br for chunk in resp for br in chunk.branches]
    assert len(branches) == 1
    assert branches[0].name == b'branch/default'
    assert branches[0].commit == branch.target_commit
    assert branches[0].commit_subject == b"Ze subject"

    resp = ref_stub.FindAllBranches(
        FindAllBranchesRequest(repository=grpc_repo))
    branches = [br for chunk in resp for br in chunk.branches]
    assert len(branches) == 1
    assert branches[0].name == b'branch/default'
    assert branches[0].target == branch.target_commit

    resp = list(ref_stub.FindAllRemoteBranches(
        FindAllRemoteBranchesRequest(repository=grpc_repo)))
    assert not resp


def test_ref_exists(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def ref_exists(ref):
        return ref_stub.RefExists(RefExistsRequest(repository=grpc_repo,
                                                   ref=ref)).value

    assert not ref_exists(b'not-a-ref-path')

    ctx = wrapper.write_commit('foo', message="Ze Foo")
    assert ref_exists(b'refs/heads/branch/default')
    assert not ref_exists(b'refs/heads/branch/other')
    assert not ref_exists(b'refs/heads/topic/default/zetop')
    assert not ref_exists(b'refs/tags/v3.2.1')

    wrapper.write_commit('zetop', topic='zetop')
    assert ref_exists(b'refs/heads/topic/default/zetop')

    wrapper.command('tag', b'v3.2.1', rev=ctx.hex())
    assert ref_exists(b'refs/tags/v3.2.1')
    assert not ref_exists(b'refs/tags/tip')

    # although we could resolve the hexadecimal node id from any
    # "wild" branch ref, it is just wrong to pretend it exists.
    assert not ref_exists(b'refs/heads/wild/' + ctx.hex())

    sref_name = b'pipelines/765'
    sref_path = b'refs/' + sref_name
    assert not ref_exists(sref_path)
    write_gitlab_special_ref(wrapper.repo, sref_name, ctx.hex())
    assert ref_exists(sref_path)

    keep_around = b'refs/keep-around/' + ctx.hex()
    assert not ref_exists(keep_around)
    create_keep_around(wrapper.repo, ctx.hex())
    assert ref_exists(keep_around)

    assert not ref_exists(b'refs/unknown/type/of/ref')


def test_delete_refs(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    repo = wrapper.repo

    def do_rpc(refs=(), except_prefixes=()):
        return ref_stub.DeleteRefs(
            DeleteRefsRequest(repository=grpc_repo,
                              refs=refs,
                              except_with_prefix=except_prefixes))

    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(refs=[b'xy'], except_prefixes=[b'refs/heads'])
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    ctx = wrapper.write_commit('foo')
    wrapper.command('tag', b'v1.2.3')

    # Deleting a branch or a tag is forbidden
    for ref in (b'branch/default',
                b'refs/heads/branch/default',
                b'refs/tags/v1.2.3'):
        assert do_rpc([ref]).git_error

    special_ref_name = b'pipelines/256'
    special_ref_path = b'refs/' + special_ref_name

    write_gitlab_special_ref(repo, special_ref_name, ctx.hex())
    # double check
    assert special_refs(repo) == {special_ref_name: ctx.hex()}

    # go (it is normal for the client-side repo to need invalidation)
    assert not do_rpc([special_ref_path]).git_error
    # TODO use the future wrapper.reload()
    setattr(repo, '_gitlab_refs_special-refs', None)
    assert special_refs(repo) == {}

    # case where one mixes unknown and known refs
    write_gitlab_special_ref(repo, special_ref_name, ctx.hex())
    # TODO use the future wrapper.reload()
    setattr(repo, '_gitlab_refs_special-refs', None)
    # double check
    assert special_refs(repo) == {special_ref_name: ctx.hex()}
    mixed_refs = [special_ref_path, b'refs/merge-requests/12/head']
    assert not do_rpc(mixed_refs).git_error

    # TODO use the future wrapper.reload()
    setattr(repo, '_gitlab_refs_special-refs', None)
    assert special_refs(repo) == {}

    other_special_ref_name = b'environments/124'
    for prefix in (b'refs/environments',
                   b'refs/environ',
                   b'refs/environments/'):
        write_gitlab_special_ref(repo, special_ref_name, ctx.hex())
        write_gitlab_special_ref(repo, other_special_ref_name, ctx.hex())
        # double check
        assert special_refs(repo) == {special_ref_name: ctx.hex(),
                                      other_special_ref_name: ctx.hex()}

        assert not do_rpc(except_prefixes=[prefix]).git_error
        # TODO use the future wrapper.reload()
        setattr(repo, '_gitlab_refs_special-refs', None)
        assert special_refs(repo) == {other_special_ref_name: ctx.hex()}

    # exclusion matching both special refs
    write_gitlab_special_ref(repo, special_ref_name, ctx.hex())
    write_gitlab_special_ref(repo, other_special_ref_name, ctx.hex())
    assert not do_rpc(except_prefixes=[b'refs/environ',
                                       b'refs/pipel']).git_error
    assert special_refs(repo) == {special_ref_name: ctx.hex(),
                                  other_special_ref_name: ctx.hex()}


def test_list_branch_names_containing_commit(grpc_channel, server_repos_root):
    """Test ListBranchNamesContainingCommit on a repo a bit more spread
    """
    ref_stub = RefServiceStub(grpc_channel)
    _, grpc_repo, changesets = make_tree_shaped_repo(server_repos_root)

    def do_list(ctx, limit=0):
        chunks_iter = ref_stub.ListBranchNamesContainingCommit(
            ListBranchNamesContainingCommitRequest(
                repository=grpc_repo,
                commit_id=pycompat.sysstr(ctx.hex()),
                limit=limit,
            ))
        return [pycompat.sysstr(gl_branch) for chunk in chunks_iter
                for gl_branch in chunk.branch_names]

    wild1, wild2 = changesets['wild1'], changesets['wild2']
    top1, top2 = changesets['top1'], changesets['top2']

    wild_branch1 = 'wild/' + pycompat.sysstr(wild1.hex())
    wild_branch2 = 'wild/' + pycompat.sysstr(wild2.hex())
    assert all(do_list(ctx) == ['topic/default/zzetop']
               for ctx in [top1, top2])
    assert do_list(wild1) == [wild_branch1]
    assert set(do_list(wild2)) == {wild_branch2, 'branch/other'}
    assert set(do_list(changesets['other_base'])) == {'branch/other',
                                                      wild_branch1,
                                                      wild_branch2,
                                                      }
    for top in (top1, top2):
        assert do_list(top) == ['topic/default/zzetop']
    assert do_list(changesets['default']) == ['branch/default']
    all_branches = {'branch/other',
                    'branch/default',
                    'topic/default/zzetop',
                    wild_branch1,
                    wild_branch2,
                    }
    base = changesets['base']
    assert set(do_list(base)) == all_branches
    limited = set(do_list(base, limit=3))
    assert len(limited) == 3
    # until we have the ordering, we can only assert sub set.
    assert limited.issubset(all_branches)


def test_list_tag_names_containing_commit(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    base = wrapper.write_commit('foo', message='Base')
    default = wrapper.write_commit('foo', message='Head of default')
    wrapper.command('tag', b'v3.2.1', rev=default.hex())

    other = wrapper.write_commit('foo', message='Start other',
                                 branch='other', parent=base)
    wrapper.command('tag', b'other-tag', rev=other.hex())

    def do_list(ctx, limit=0):
        chunks_iter = ref_stub.ListTagNamesContainingCommit(
            ListTagNamesContainingCommitRequest(
                repository=grpc_repo,
                commit_id=pycompat.sysstr(ctx.hex()),
                limit=limit,
            ))
        return [pycompat.sysstr(tag_name) for chunk in chunks_iter
                for tag_name in chunk.tag_names]

    all_tags = {'v3.2.1', 'other-tag'}
    assert set(do_list(base)) == all_tags
    assert do_list(default) == ['v3.2.1']
    assert do_list(other) == ['other-tag']

    limited = do_list(base, limit=1)
    assert len(limited) == 1
    assert limited[0] in all_tags


def test_get_tags_messages(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    wrapper.write_commit('foo', message='Base')
    wrapper.command('tag', b'v3.2.1', rev=b'.',
                    message=b"The tag message")
    tag_hex = wrapper.repo[b'tip'].hex()

    def do_list(tag_ids):
        resp_iter = ref_stub.GetTagMessages(
            GetTagMessagesRequest(
                repository=grpc_repo,
                tag_ids=(pycompat.sysstr(tag_id) for tag_id in tag_ids),
            ))
        return [pycompat.sysstr(resp.message) for resp in resp_iter]

    assert do_list([tag_hex]) == ["The tag message"]


def test_pack_refs(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    resp = ref_stub.PackRefs(PackRefsRequest(repository=grpc_repo))
    assert resp == PackRefsResponse()


def test_find_ref_name(grpc_channel, server_repos_root, monkeypatch):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root,
                                         extra_extensions=('heptapod',
                                                           'hggit'))

    base_ctx = wrapper.write_commit('foo', message="base")
    base_sha = base_ctx.hex()
    default_sha = wrapper.write_commit('foo', message="default").hex()

    other_sha = wrapper.write_commit('foo', message="other",
                                     branch="other",
                                     parent=base_ctx).hex()

    # This will have to be removed when we don't have hg_git projects
    # any more, but at this point, ensure_gitlab_branches can be taken
    # for granted
    wrapper.repo.ui.environ[b'HEPTAPOD_SKIP_ALL_GITLAB_HOOKS'] = b'yes'
    wrapper.set_config('heptapod', 'gitlab-internal-api-secret-file',
                       'matters-in-hook-constructor-only')
    wrapper.command('gitlab-mirror')

    def do_rpc(commit_id, prefix):
        return ref_stub.FindRefName(FindRefNameRequest(repository=grpc_repo,
                                                       commit_id=commit_id,
                                                       prefix=prefix))

    # response is the first in alphabetical order, hence default branch
    # is expected for base changeset because 'default' < 'other'
    for prefix in (b'refs/heads',
                   b'refs/heads/',
                   b'refs/heads/branch',
                   b'refs/heads/branch/',
                   b'refs/heads/branch/default',
                   ):

        assert do_rpc(base_sha, prefix).name == b'refs/heads/branch/default'
        assert do_rpc(default_sha, prefix).name == b'refs/heads/branch/default'

    for prefix in (b'refs/heads',
                   b'refs/heads/',
                   b'refs/heads/branch',
                   b'refs/heads/branch/',
                   b'refs/heads/branch/other',
                   ):

        assert do_rpc(other_sha, prefix).name == b'refs/heads/branch/other'

    for prefix in (b'refs/heads/bra',
                   b'refs/heads/branch/def',
                   ):
        assert not do_rpc(base_sha, prefix).name
        assert not do_rpc(default_sha, prefix).name

    wrapper.command('tag', b'zzz', rev=default_sha)
    wrapper.command('tag', b'yyy/1', rev=other_sha)

    # again, first match in alphabetical order
    assert do_rpc(base_sha, b'refs/tags').name == b'refs/tags/yyy/1'
    assert do_rpc(base_sha, b'refs/tags/yyy').name == b'refs/tags/yyy/1'
    assert do_rpc(base_sha, b'refs/tags/zzz').name == b'refs/tags/zzz'

    assert not do_rpc(other_sha, b'refs/tags/yy').name
    assert do_rpc(other_sha, b'refs/tags/yyy').name == b'refs/tags/yyy/1'
    assert do_rpc(other_sha, b'refs/tags/yyy/1').name == b'refs/tags/yyy/1'

    # and of course alphabetical order dictatest that branches match
    # before tags if the prefix doesn't discriminate ref types
    assert do_rpc(base_sha, b'refs').name == b'refs/heads/branch/default'

    # error cases (using full length SHAs for unknown changeset IDs
    # to rule out other reasons than really not found)
    assert not do_rpc('12de34ad' * 5, b'refs').name

    unknown_sha = '5678cafe' * 5

    # invalid entry is just ignored, be it in favor of other type of ref
    # or within the same type
    write_gitlab_branches(wrapper.repo,
                          {b'branch/default': unknown_sha.encode()})
    assert do_rpc(base_sha, b'refs').name == b'refs/tags/yyy/1'

    write_gitlab_branches(wrapper.repo,
                          {b'branch/default': unknown_sha.encode(),
                           b'branch/other': other_sha})
    assert do_rpc(base_sha, b'refs/heads').name == b'refs/heads/branch/other'
