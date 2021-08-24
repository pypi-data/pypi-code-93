# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from mercurial import (
    error,
    node as nodemod,
    pycompat,
)
from hgext3rd.evolve import headchecking
from heptapod.gitlab.branch import (
    branchmap_branch_from_gitlab_branch,
    gitlab_branch_from_branchmap_branch,
    parse_wild_gitlab_branch,
    gitlab_branch_ref,
)
from hgext3rd.heptapod.branch import (
    GITLAB_BRANCHES_MISSING,
    get_default_gitlab_branch,
    gitlab_branches,
)
from hgext3rd.heptapod import (
    ensure_gitlab_branches as hg_git_ensure_gitlab_branches,
)

import logging
logger = logging.getLogger(__name__)


def _extract_branchmap_heads(repo, entry,
                             avoid_bookmark_shadowing=False):
    """From the given branchmap entry, extract default head and list of heads.

    The default head is what needs to be returned for a simple branchmap
    branch lookup. It can be ``None`` if all heads are invisible to GitLab
    (closed or bookmarked).

    :param avoid_bookmark_shadowing: if ``True`` the bookmarked revision with
       the highest revno can be returned if there's nothing else
    :return: (default head, all heads visible to GitLab), all given as
             :class:`changectx` instances.
    """
    # branchmap entries results are already sorted by increasing rev number
    revs = [repo[node].rev() for node in entry]
    contexts = (repo[rev]
                for rev in headchecking._filter_obsolete_heads(repo, revs))
    visible = [c for c in contexts if not (c.closesbranch() or c.bookmarks())]

    if not visible and avoid_bookmark_shadowing:
        # rare case, performance is irrelevant, we can re-lookup
        for ctx in (repo[node] for node in reversed(entry)):
            if not ctx.obsolete() and not ctx.closesbranch():
                return ctx, [ctx]

    if not visible:
        return None, visible

    return visible[-1], visible


def changeset_branchmap_entry(repo, ctx):
    """Return the branchmap entry for branch/topic combination of a changeset

    :param ctx: the changeset, given as a :class:`changectx`.
    """
    branch, topic = ctx.branch(), ctx.topic()
    key = branch if not topic else b':'.join((branch, topic))
    return repo.branchmap()[key]


def gitlab_branch_head(repo, gl_branch):
    """Return the unique head of the given GitLab branch.

    Does not resolve other types of "revisions".

    :return: a :class:`changectx` or ``None`` if there's no changeset for
             the given ``gl_branch``.
    """
    gl_branches = gitlab_branches(repo)
    if gl_branches is not GITLAB_BRANCHES_MISSING:
        sha = gl_branches.get(gl_branch)
        if sha is None:
            return None
        return repo[sha]

    logger.warning("gitlab_branch_head for %r: no GitLab branches state file "
                   "defaulting to slow direct analysis.", repo.root)
    wild_hex = parse_wild_gitlab_branch(gl_branch)
    if wild_hex is not None:
        wild_bin = nodemod.bin(wild_hex)
        try:
            wild_ctx = repo[wild_bin]
        except error.RepoLookupError:
            return None

        if wild_ctx.bookmarks():
            # a bookmarked head is never wild
            return None

        heads = _extract_branchmap_heads(
            repo, changeset_branchmap_entry(repo, wild_ctx))[1]
        return wild_ctx if len(heads) > 1 and wild_ctx in heads else None

    branchmap_key = branchmap_branch_from_gitlab_branch(gl_branch)
    if branchmap_key is not None:
        try:
            entry = repo.branchmap()[branchmap_key]
        except KeyError:
            return None
        return _extract_branchmap_heads(
            repo, entry,
            avoid_bookmark_shadowing=(
                gl_branch == get_default_gitlab_branch(repo)),
        )[0]

    # last chance: bookmarks
    bookmark_node = repo._bookmarks.get(gl_branch)
    if bookmark_node is None:
        return None
    return repo[bookmark_node]


def iter_gitlab_branches(repo):
    """Iterate on all visible GitLab branches

    Each iteration yields a pair ``(gl_branch, head)`` where ``gl_branch``
    is the name of the GitLab branch and ``head`` is a :class:`changectx`
    instance.
    """
    gl_branches = gitlab_branches(repo)
    if gl_branches is not GITLAB_BRANCHES_MISSING:
        for branch, sha in gl_branches.items():
            try:
                yield branch, repo[sha]
            except error.RepoLookupError as exc:
                logger.error("Unknown changeset ID in GitLab branches "
                             "statefile for repo at %r: %r",
                             repo.root, exc)
    else:
        logger.warning("iter_gitlab_branches for %r: "
                       "no GitLab branches state file "
                       "defaulting to slow direct analysis.", repo.root)
        for branch, ctx in iter_compute_gitlab_branches(repo):
            yield branch, ctx


def iter_compute_gitlab_branches(repo):
    """Generator that computes GitLab branches from scratch"""
    for key, entry in pycompat.iteritems(repo.branchmap()):
        gl_branch = gitlab_branch_from_branchmap_branch(key)
        default, visible = _extract_branchmap_heads(
            repo, entry,
            avoid_bookmark_shadowing=(
                gl_branch == get_default_gitlab_branch(repo)))
        if not visible:
            continue

        yield gl_branch, default
        if len(visible) > 1:
            for head in visible:
                yield b'wild/' + head.hex(), head

    for key, node in pycompat.iteritems(repo._bookmarks):
        yield key, repo[node]


def iter_gitlab_branches_as_refs(repo):
    """Same as :func:`iter_gitlab_branches`, yielding full Git refs."""
    for branch, ctx in iter_gitlab_branches(repo):
        yield gitlab_branch_ref(branch), ctx


def ensure_gitlab_branches_state_file(repo):
    """Make sure that the GitLab branches state file exists.

    Some implementations have to rely on it, and we will soon basically
    require in in practice, lest the performance degradation become
    intolerable.

    For now, we can assume that all repositories are actually handled with
    the mirroring to Git code from hgext3rd.heptapod.

    When that becomes false, we'll be faced with two options:

    - have enough trust in our migration scenarios that we simply make it
      a hard requirement or
    - keep the code able to recompute all GitLab branches around, such as
      :func:`gitlab_branch_head` as of this writing and use it to reconstruct
      the file.

    See also py-heptapod#8
    """
    hg_git_ensure_gitlab_branches(repo.ui, repo)
