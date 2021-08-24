# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from heptapod.testhelpers import (
    LocalRepoWrapper,
)

from ..branch import (
    gitlab_branch_head,
    iter_gitlab_branches,
)

from hgext3rd.heptapod.branch import (
    set_default_gitlab_branch,
    write_gitlab_branches,
)


def make_repo(path):
    return LocalRepoWrapper.init(path,
                                 config=dict(
                                     extensions=dict(topic=''),
                                 ))


def test_named_branch_multiple_heads(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    default_branch = b'branch/default'

    # no head, no bookmark
    assert gitlab_branch_head(repo, default_branch) is None
    assert gitlab_branch_head(repo, b'zebook') is None

    # one head
    base = wrapper.write_commit('foo')
    assert gitlab_branch_head(repo, default_branch) == base
    assert list(iter_gitlab_branches(repo)) == [(default_branch, base)]

    # two heads, no bookmark
    head1 = wrapper.write_commit('foo')
    head2 = wrapper.write_commit('foo', parent=base)

    assert gitlab_branch_head(repo, default_branch) == head2
    assert set(iter_gitlab_branches(repo)) == {
        (default_branch, head2),
        (b'wild/' + head1.hex(), head1),
        (b'wild/' + head2.hex(), head2),
    }
    assert gitlab_branch_head(repo, b'wild/' + head1.hex()) == head1
    assert gitlab_branch_head(repo, b'wild/' + head2.hex()) == head2

    # one bookmarked head and one not bookmarked
    wrapper.command('bookmark', b'book2', rev=head2.hex())
    assert gitlab_branch_head(repo, default_branch) == head1
    assert set(iter_gitlab_branches(repo)) == {
        (default_branch, head1),
        (b'book2', head2),
    }
    assert gitlab_branch_head(repo, b'wild/' + head1.hex()) is None
    assert gitlab_branch_head(repo, b'wild/' + head2.hex()) is None
    assert gitlab_branch_head(repo, b'book2') == head2

    # all heads bookmarked
    wrapper.command('bookmark', b'book1', rev=head1.hex())
    assert gitlab_branch_head(repo, default_branch) is None
    assert set(iter_gitlab_branches(repo)) == {
        (b'book1', head1),
        (b'book2', head2),
    }

    # finally, a formally correct wild branch, with no corresponding changeset
    assert gitlab_branch_head(repo, b'wild/' + (b'cafe' * 10)) is None


def test_invalid_state_file_entry(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo
    ctx = wrapper.write_commit('foo')

    # invalid entry is just ignored, be it in favor of other type of ref
    # or within the same type
    write_gitlab_branches(repo,
                          {b'branch/default': ctx.hex(),
                           b'invalid': b'1234beef' * 5})
    assert list(iter_gitlab_branches(repo)) == [(b'branch/default', ctx)]


def test_bookmarks_not_shadowing_default_branch(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo
    base = wrapper.write_commit('foo')  # not strictly necessary
    head1 = wrapper.write_commit('foo')

    default_branch = b'branch/default'
    set_default_gitlab_branch(repo, default_branch)

    wrapper.command('bookmark', b'book1', rev=head1.hex())
    assert gitlab_branch_head(repo, default_branch) == head1

    head2 = wrapper.write_commit('foo', parent=base)
    wrapper.command('bookmark', b'book2', rev=head2.hex())

    assert gitlab_branch_head(repo, default_branch) == head2
    assert set(iter_gitlab_branches(repo)) == {
        (b'book1', head1),
        (b'book2', head2),
        (default_branch, head2)
    }


def test_gitlab_branches_state_file(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    base = wrapper.commit_file('foo')
    default = wrapper.commit_file('foo')
    topic = wrapper.commit_file('foo', parent=base, topic='zztop')

    write_gitlab_branches(wrapper.repo,
                          {b'branch/default': default.hex(),
                           b'topic/default/zztop': topic.hex(),
                           })

    assert gitlab_branch_head(repo, b'branch/default') == default
    assert gitlab_branch_head(repo, b'branch/typo') is None

    assert dict(iter_gitlab_branches(repo)) == {
        b'branch/default': default,
        b'topic/default/zztop': topic,
    }
