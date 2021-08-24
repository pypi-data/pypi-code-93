# Copyright 2020-2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging

from hgext3rd.heptapod.branch import get_default_gitlab_branch
from google.protobuf.timestamp_pb2 import Timestamp
from mercurial import (
    util,
    error,
    pycompat,
    logcmdutil,
    hgweb,
)

from .. import manifest
from ..errors import (
    failed_precondition,
    internal_error,
    invalid_argument,
    not_implemented,
)
from ..stub.commit_pb2 import (
    CommitIsAncestorRequest,
    CommitIsAncestorResponse,
    TreeEntryRequest,
    TreeEntryResponse,
    CommitsBetweenRequest,
    CommitsBetweenResponse,
    CountCommitsRequest,
    CountCommitsResponse,
    CountDivergingCommitsRequest,
    CountDivergingCommitsResponse,
    GetTreeEntriesRequest,
    GetTreeEntriesResponse,
    TreeEntry,
    ListFilesRequest,
    ListFilesResponse,
    FindCommitRequest,
    FindCommitResponse,
    CommitStatsRequest,
    CommitStatsResponse,
    FindAllCommitsRequest,
    FindAllCommitsResponse,
    FindCommitsRequest,
    FindCommitsResponse,
    CommitLanguagesRequest,
    CommitLanguagesResponse,
    RawBlameRequest,
    RawBlameResponse,
    LastCommitForPathRequest,
    LastCommitForPathResponse,
    ListLastCommitsForTreeRequest,
    ListLastCommitsForTreeResponse,
    CommitsByMessageRequest,
    CommitsByMessageResponse,
    ListCommitsByOidRequest,
    ListCommitsByOidResponse,
    ListCommitsByRefNameRequest,
    ListCommitsByRefNameResponse,
    FilterShasWithSignaturesRequest,
    FilterShasWithSignaturesResponse,
    GetCommitSignaturesRequest,
    GetCommitSignaturesResponse,
    GetCommitMessagesRequest,
    GetCommitMessagesResponse,
)
from ..stub.commit_pb2_grpc import CommitServiceServicer

from .. import message
from ..oid import (
    tree_oid,
    blob_oid,
)
from ..revision import gitlab_revision_changeset
from ..servicer import HGitalyServicer
from ..git import (
    OBJECT_MODE_TREE,
)
from ..file_context import (
    git_perms,
)
from ..util import chunked
from ..stream import (
    concat_resplit,
    WRITE_BUFFER_SIZE,
)

logger = logging.getLogger(__name__)


class CommitServicer(CommitServiceServicer, HGitalyServicer):

    def CommitIsAncestor(self,
                         request: CommitIsAncestorRequest,
                         context) -> CommitIsAncestorResponse:
        logger.debug("Processing %r", message.Logging(request))
        # The question is legit for filtered changesets and that
        # happens in MR rebase scenarios, before the Rails app realizes
        # the MR has to be updated.
        repo = self.load_repo(request.repository, context).unfiltered()
        # TODO status.Errorf(codes.InvalidArgument, "Bad Request
        # (empty ancestor sha)") and same for child
        try:
            ancestor = repo[request.ancestor_id.encode()]
            child = repo[request.child_id.encode()]
        except error.RepoLookupError as exc:
            # Gitaly just returns False. This is probably an inconsistency
            # in the client, so let's log it to help.
            logger.warning(
                "CommitIsAncestor for child_id=%r, ancestor_id=%r, got %r",
                request.ancestor_id, request.child_id, exc)
            result = False
        else:
            result = ancestor.isancestorof(child)

        return CommitIsAncestorResponse(value=result)

    def TreeEntry(self, request: TreeEntryRequest,
                  context) -> TreeEntryResponse:
        """Return an entry of a tree.

        The name could be confusing with the entry for a tree.
        Actually, it always yields one response message, using the empty
        response in case the given path does not resolve.
        """
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context).unfiltered()
        changeset = gitlab_revision_changeset(repo, request.revision)
        if changeset is None:
            # unknown revision is not an error, and expected in some cases.
            yield TreeEntryResponse()
            return

        sha = changeset.hex().decode('ascii')
        # early testing shows that even for leaf files, Gitaly ignores
        # trailing slashes
        path = request.path.rstrip(b'/')

        try:
            filectx = changeset.filectx(path)
        except error.ManifestLookupError:
            filectx = None

        if filectx is not None:
            otype = TreeEntryResponse.ObjectType.BLOB
            oid = blob_oid(repo, sha, path)
            mode = git_perms(filectx)
            size = filectx.size()
            max_size = request.max_size
            if max_size != 0 and size > request.max_size:
                yield failed_precondition(
                    context, TreeEntryResponse,
                    "TreeEntry: object size (%d) is bigger than the maximum "
                    "allowed size (%d)" % (size, max_size))
                return

            data = filectx.data()
            limit = request.limit
            if limit != 0:
                data = data[:limit]

            offset = 0
            while offset <= size:
                yield TreeEntryResponse(
                    type=otype,
                    oid=oid,
                    size=size,
                    data=data[offset:offset+WRITE_BUFFER_SIZE],
                    mode=mode)
                offset += WRITE_BUFFER_SIZE
            return

        subtrees, file_paths = manifest.miner(changeset).ls_dir(path)
        if not subtrees and not file_paths:
            yield TreeEntryResponse()
            return

        # path is an actual directory

        # size computation to match Git response.
        # The formula for size computation is meant to match the size
        # returned by Git, which is actually the size of the raw Git Tree
        # object as returned by `git-cat-file` with `<type>` parameter.
        #
        # The raw Git Tree object is a simple concatenation of entries, each
        # one being made of
        # - mode (octal representation): 6 bytes for blobs (e.g 100644),
        #                                5 bytes for subtrees (40000)
        # - 0x20 (separator): 1 byte
        # - name of the entry
        # - 0x00 (separator): 1 byte
        # - binary SHA-1 of the object referenced by the entry: 20 bytes
        # Hence the total length per entry is 27 + (name length) for subtrees
        # and 28 + (name length) for blobs.
        # Finally, our `ls_dir` returns full paths from the root, so the
        # have to substract `len(path + b'/')`, hence `len(path) + 1`
        # for each entry.
        size = (
            28 * len(file_paths) + 27 * len(subtrees)
            + sum(len(s) for s in subtrees) + sum(len(f) for f in file_paths)
            - (len(subtrees) + len(file_paths)) * (len(path) + 1)
        )
        # max_size does not apply here (see Gitaly comparison test)
        yield TreeEntryResponse(
            type=TreeEntryResponse.ObjectType.TREE,
            oid=tree_oid(repo, sha, path),
            mode=OBJECT_MODE_TREE,
            size=size,
        )

    def CommitsBetween(self,
                       request: CommitsBetweenRequest,
                       context) -> CommitsBetweenResponse:
        """Stream chunks of commits "between" two GitLab revisions.

        One may believe the meaning of "between" to be based on DAG ranges,
        but actually, what the Gitaly reference Golang implementation does is
        ``git log --reverse FROM..TO``, which is indeed commonly used to obtain
        exclusive DAG ranges (would be `FROM::TO - FROM`) but gitrevisions(1)
        actually says:
           you can ask for commits that are reachable
           from r2 excluding those that are reachable from r1 by ^r1 r2
           and it can be written as r1..r2.

        So the true Mercurial equivalent revset is actually `TO % FROM`,
        which is quite different if FROM is not an ancestor of TO.

        Sadly, we happen to know `%` to be less efficient than DAG ranges.

        TODO: assuming the most common use case is indeed to obtain DAG ranges,
        (for which GitLab would actually have to check ancestry first), maybe
        introduce a direct call for DAG ranges later.
        TODO: find out if there are default values to apply for ``from`` and
              ``to``
        """
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        unfi = repo.unfiltered()
        rev_from = gitlab_revision_changeset(repo, getattr(request, 'from'))
        rev_to = gitlab_revision_changeset(repo, getattr(request, 'to'))

        # logging potentially both resolution failures
        if rev_from is None:
            logger.warning("cannot resolve 'from' revision in %r",
                           message.Logging(request))
        if rev_to is None:
            logger.warning("cannot resolve 'to' revision in %r",
                           message.Logging(request))

        if rev_from is None or rev_to is None:
            revs = []
        else:
            revs = unfi.revs('only(%s, %s)', rev_to, rev_from)

        for chunk in chunked(revs):
            yield CommitsBetweenResponse(
                commits=(message.commit(unfi[rev]) for rev in chunk))

    def CountCommits(self,
                     request: CountCommitsRequest,
                     context) -> CountCommitsResponse:
        logger.debug("Processing %r", message.Logging(request))
        # TODO: yet to finish this method to support all lookups
        repo = self.load_repo(request.repository, context)
        revision = request.revision
        # revision can be a pseudo range, like b'12340f9b5..a5f36b6a53012',
        # (see CommitsBetween for how we handle that)
        # (used in MR widget)
        if revision:
            if b'..' in revision:
                # TODO also case of ... (3 dots), I suppose
                ctx_start, ctx_end = [gitlab_revision_changeset(repo, rev)
                                      for rev in revision.split(b'..')]
                if ctx_start is None or ctx_end is None:
                    logger.warning(
                        "CountCommits for %r: one of these revisions "
                        "could not be found", revision)
                    return CountCommitsResponse()

                revs = repo.revs('only(%s, %s)', ctx_end, ctx_start)
            else:
                ctx = gitlab_revision_changeset(repo, revision)
                if ctx is None:
                    logger.warning(
                        "CountCommits revision %r could not be found",
                        revision)
                    return CountCommitsResponse()
                revs = repo.revs('::%s', ctx)
            count = len(revs)
        else:
            # Note: if revision is not passed, we return all revs for now.
            # `revision` and `all` are mutually exclusive
            count = len(repo)
        max_count = request.max_count
        if max_count and count > max_count:
            count = max_count
        return CountCommitsResponse(count=count)

    # CountDivergingCommits counts the diverging commits between from and to.
    # Important to note that when --max-count is applied, the counts are not
    # guaranteed to be accurate.

    def CountDivergingCommits(self,
                              request: CountDivergingCommitsRequest,
                              context) -> CountDivergingCommitsResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        rev_from = gitlab_revision_changeset(repo, getattr(request, 'from'))
        rev_to = gitlab_revision_changeset(repo, getattr(request, 'to'))
        max_count = request.max_count
        if rev_from is None:
            logger.warning("cannot resolve 'from' revision in %r",
                           message.Logging(request))
        if rev_to is None:
            logger.warning("cannot resolve 'to' revision in %r",
                           message.Logging(request))
        if rev_from is None or rev_to is None:
            return CountDivergingCommitsResponse(left_count=0, right_count=0)
        left = rev_from.rev()
        right = rev_to.rev()
        branchpoint = repo.revs(b"ancestor(%d, %d)" % (left, right)).first()
        left_count = len(repo.revs(b"%d::%d - %d" %
                                   (branchpoint, left, branchpoint)))
        right_count = len(repo.revs(b"%d::%d - %d" %
                                    (branchpoint, right, branchpoint)))
        if max_count and (left_count + right_count) > max_count:
            delta = (left_count + right_count) - max_count
            if left_count >= delta:
                left_count -= delta
            else:
                delta -= left_count
                left_count = 0
                right_count -= delta
        return CountDivergingCommitsResponse(left_count=left_count,
                                             right_count=right_count)

    def GetTreeEntries(self, request: GetTreeEntriesRequest,
                       context) -> GetTreeEntriesResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context).unfiltered()
        revision = request.revision
        changeset = gitlab_revision_changeset(repo, revision)
        sha = changeset.hex().decode('ascii')
        path = request.path.rstrip(b'/')  # same as in TreeEntry
        if path == b'.':  # special case, means the top directory
            path = b''

        blob_type = TreeEntry.EntryType.BLOB
        tree_type = TreeEntry.EntryType.TREE
        root_oid = tree_oid(repo, sha, b'')
        miner = manifest.miner(changeset)

        if request.recursive:
            entries = ((epath, is_dir, b'')
                       for epath, is_dir in miner.iter_dir_recursive(path))
        else:
            entries = miner.iter_dir_with_flat_paths(path)
        for chunk in chunked(entries):
            yield GetTreeEntriesResponse(
                entries=(
                    TreeEntry(
                        path=path,
                        type=tree_type if is_dir else blob_type,
                        oid=(tree_oid(repo, sha, path) if is_dir
                             else blob_oid(repo, sha, path)),
                        commit_oid=revision,
                        root_oid=root_oid,
                        mode=(OBJECT_MODE_TREE if is_dir else
                              git_perms(changeset.filectx(path))),
                        flat_path=flat_path,
                    )
                    for path, is_dir, flat_path in chunk)
            )

    def ListFiles(self, request: ListFilesRequest,
                  context) -> ListFilesResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        revision = pycompat.sysbytes(request.revision)
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None:
            return
        mf = ctx.manifest()
        for paths in chunked(mf.iterkeys()):
            yield ListFilesResponse(paths=paths)

    def CommitStats(self, request: CommitStatsRequest,
                    context) -> CommitStatsResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        revision = pycompat.sysbytes(request.revision)
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None:
            return internal_error(
                context, CommitStatsResponse,
                "failed to get commit stats: object not found.",
                log_level=logging.WARNING
            )
        ctxp1 = ctx.p1()
        statsgen = hgweb.webutil.diffstatgen(repo.ui, ctx, ctxp1)
        # stats format:
        #   (list_of_stats_per_file, maxname,
        #    maxtotal, addtotal, removetotal, binary)
        # we only need addtotal and removetotal for our use case
        stats = next(statsgen)
        addtotal, removetotal = stats[-3], stats[-2]
        return CommitStatsResponse(
            oid=ctx.hex(),
            additions=addtotal,
            deletions=removetotal,
        )

    def FindCommit(self,
                   request: FindCommitRequest, context) -> FindCommitResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        revision = request.revision
        ctx = gitlab_revision_changeset(repo, revision)

        if ctx is None:
            logger.warning(
                "FindCommit revision %r could not be found",
                revision)
            return FindCommitResponse()

        commit = message.commit(ctx)
        return FindCommitResponse(commit=commit)

    def FindAllCommits(self, request: FindAllCommitsRequest,
                       context) -> FindAllCommitsResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        revision = request.revision
        opts = {}
        if revision:
            # If false, return all commits reachable by any branch in the repo
            ctx = gitlab_revision_changeset(repo, revision)
            if ctx is None:
                logger.debug(
                    "FindAllCommits revision %r could not be found",
                    revision)
                return FindAllCommitsResponse()
            revset = b"reverse(::%s)" % ctx
            opts[b'rev'] = [revset]
            # if ctx is an obsolete changeset, its repo is unfiltered.
            # this is legitimate if revision is a direct hash and should
            # not happen otherwise
            repo = ctx.repo()
        # gracinet: when we remove that compat, we can simply
        # just use repos.revs(), since logcmdutil does not seem to be
        # useful for this case (no `pats`) and is obviously a compatibility
        # hazard in itself.
        if util.versiontuple(n=2) <= (5, 5):
            revs, _ = logcmdutil.getrevs(repo, pats=(), opts=opts)  # hg<=5.5
        else:  # hg>5.5
            walk_opts = logcmdutil.parseopts(repo.ui, pats=(), opts=opts)
            revs, _ = logcmdutil.getrevs(repo, walk_opts)
        offset = request.skip
        if offset and offset > 0:
            revs = revs.slice(offset, len(revs))
        if request.max_count:
            revs = revs.slice(0, request.max_count)
        if request.order == FindAllCommitsRequest.TOPO:
            revs = repo.revs(b"sort(%ld, topo)", revs)
        elif request.order == FindAllCommitsRequest.DATE:
            revs = repo.revs(b"reverse(sort(%ld, date))", revs)
        for chunk in chunked(revs):
            yield FindAllCommitsResponse(
                commits=(message.commit(repo[rev]) for rev in chunk))

    def FindCommits(self, request: FindCommitsRequest,
                    context) -> FindCommitsResponse:

        req_log = message.Logging(request)
        logger.debug("Processing %r", message.Logging(request))

        if request.limit == 0:
            return

        repo = self.load_repo(request.repository, context)
        pats = request.paths
        # XXX: raise error if one of the path given is an empty string
        if pats:
            pats = list(map(lambda p: repo.root + b'/' + p, pats))

        opts = parse_find_commits_request_opts(request, repo)

        if request.revision and not opts[b'rev'][0]:
            logger.debug(
                "Request %r, revision could not be found", req_log)
            return FindCommitsResponse()

        if util.versiontuple(n=2) <= (5, 5):  # hg<=5.5
            if request.follow and opts.get(b'rev'):
                # Mercurial 5.5: 'follow' option of `hg log` doesn't work
                # well when --rev option is set. For e.g. try
                # `hg log <file> --follow -r 'all()'`
                del opts[b'rev']
            revs, _ = logcmdutil.getrevs(repo, pats, opts)
        else:  # hg>5.5
            walk_opts = logcmdutil.parseopts(repo.ui, pats, opts)
            revs, _ = logcmdutil.getrevs(repo, walk_opts)

        if request.offset > 0:
            revs = revs.slice(request.offset, len(revs))

        if request.order == FindCommitsRequest.TOPO:
            revs = repo.revs(b"sort(%ld, topo)", revs)
            if request.all:
                revs = repo.revs(b"reverse(%ld)", revs)

        for chunk in chunked(revs):
            yield FindCommitsResponse(
                commits=(message.commit(repo[rev]) for rev in chunk))

    def CommitLanguages(self, request: CommitLanguagesRequest,
                        context) -> CommitLanguagesResponse:
        return not_implemented(context, CommitLanguagesResponse,
                               issue=12)  # pragma no cover

    def RawBlame(self, request: RawBlameRequest,
                 context) -> RawBlameResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        filepath = request.path
        if not filepath:
            yield invalid_argument(context, RawBlameResponse,
                                   "RawBlame: empty Path")
            return
        revision = pycompat.sysbytes(request.revision)
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None:
            return
        for data in concat_resplit(blamelines(repo, ctx, filepath),
                                   WRITE_BUFFER_SIZE):
            yield RawBlameResponse(data=data)

    def LastCommitForPath(self,
                          request: LastCommitForPathRequest,
                          context) -> LastCommitForPathResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        revision, path = request.revision, request.path
        ctx = gitlab_revision_changeset(repo, revision)
        changeset = latest_changeset_for_path(path, ctx)
        return LastCommitForPathResponse(commit=message.commit(changeset))

    def ListLastCommitsForTree(self, request: ListLastCommitsForTreeRequest,
                               context) -> ListLastCommitsForTreeResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        revision = pycompat.sysbytes(request.revision)
        from_ctx = gitlab_revision_changeset(repo, revision)
        if from_ctx is None:
            yield internal_error(context, ListLastCommitsForTreeResponse,
                                 "exit status 128")
            return

        offset, limit = request.offset, request.limit
        if limit == 0:
            return

        if limit < 0:
            yield invalid_argument(context, ListLastCommitsForTreeResponse,
                                   'limit negative')
        if offset < 0:
            yield invalid_argument(context, ListLastCommitsForTreeResponse,
                                   'offset negative')

        req_path = request.path

        if req_path in (b'.', b'/', b'./'):
            req_path = b''

        if req_path and not req_path.endswith(b'/'):
            if offset > 0:
                return

            changeset = latest_changeset_for_path(req_path, from_ctx)
            yield ListLastCommitsForTreeResponse(
                commits=[message.commit_for_tree(changeset, req_path)])
            return

        # subtrees first, then regular files, each one in lexicographical order
        subtrees, file_paths = manifest.miner(from_ctx).ls_dir(req_path)
        all_paths = subtrees
        all_paths.extend(file_paths)

        for chunk in chunked(all_paths[offset:offset + limit]):
            yield ListLastCommitsForTreeResponse(
                commits=[
                    message.commit_for_tree(
                        latest_changeset_for_path(path, from_ctx),
                        path
                    )
                    for path in chunk
                ])

    def CommitsByMessage(self, request: CommitsByMessageRequest,
                         context) -> CommitsByMessageResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        query = request.query
        if not query:
            return CommitsByMessageResponse()
        pats = []
        opts = {}
        if request.path:
            path = repo.root + b'/' + request.path
            pats.append(path)
        if request.limit:
            opts[b'limit'] = request.limit
        if request.revision:
            revset = revset_from_gitlab_revision(repo, request.revision)
            if revset is None:
                logger.debug(
                    "CommitsByMessage revision %r could not be found",
                    request.revision)
                return CommitsByMessageResponse()
        else:
            revision = get_default_gitlab_branch(repo)
            # XXX: return error if no default branch found
            revset = revset_from_gitlab_revision(repo, revision)
        # Instead of sending 'query' as a key:value pair ('keyword': query) in
        # `opts`, appending the query to `revset` as "...and keyword('query')"
        # to make sure it perform an intersetion of two, instead of a union.
        revset = revset + b" and keyword('%b')" % query.encode()
        opts[b'rev'] = [revset]
        if util.versiontuple(n=2) <= (5, 5):  # hg<=5.5
            revs, _ = logcmdutil.getrevs(repo, pats, opts)
        else:  # hg>5.5
            walk_opts = logcmdutil.parseopts(repo.ui, pats, opts)
            revs, _ = logcmdutil.getrevs(repo, walk_opts)
        offset = request.offset
        if offset and offset > 0:
            revs = revs.slice(offset, len(revs))
        for chunk in chunked(revs):
            yield CommitsByMessageResponse(
                commits=(message.commit(repo[rev]) for rev in chunk))

    def ListCommitsByOid(self, request: ListCommitsByOidRequest,
                         context) -> ListCommitsByOidResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        lookup_error_classes = (error.LookupError, error.RepoLookupError)
        for chunk in chunked(pycompat.sysbytes(oid) for oid in request.oid):
            try:
                chunk_commits = [message.commit(repo[rev])
                                 for rev in repo.revs(b'%ls', chunk)]
            except lookup_error_classes:
                # lookup errors aren't surprising: the client uses this
                # method for prefix resolution
                # The reference Gitaly implementation tries them one after
                # the other (as of v13.4.6)
                chunk_commits = []
                for oid in chunk:
                    try:
                        # TODO here, something only involving the nodemap
                        # would be in order
                        revs = repo.revs(b'%s', oid)
                    except lookup_error_classes:
                        # ignore unresolvable oid prefix
                        pass
                    else:
                        if len(revs) == 1:
                            chunk_commits.append(
                                message.commit(repo[revs.first()]))
            yield ListCommitsByOidResponse(commits=chunk_commits)

    def ListCommitsByRefName(self, request: ListCommitsByRefNameRequest,
                             context) -> ListCommitsByRefNameResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        ref_names = request.ref_names

        commits = []
        for ref_name in ref_names:
            ctx = gitlab_revision_changeset(repo, ref_name)
            if ctx is None:
                logger.warning(
                    "ListCommitByRefName ref %r could not be "
                    "resolved to a changeset",
                    ref_name)
                continue
            commits.append([ref_name, ctx])
        CommitForRef = ListCommitsByRefNameResponse.CommitForRef
        for chunk in chunked(commits):
            yield ListCommitsByRefNameResponse(
                commit_refs=(CommitForRef(
                    commit=message.commit(ctx),
                    ref_name=ref_name
                ) for ref_name, ctx in chunk)
            )

    def FilterShasWithSignatures(self,
                                 request: FilterShasWithSignaturesRequest,
                                 context) -> FilterShasWithSignaturesResponse:
        return not_implemented(context, FilterShasWithSignaturesResponse,
                               issue=24)  # pragma no cover

    def GetCommitSignatures(self, request: GetCommitSignaturesRequest,
                            context) -> GetCommitSignaturesResponse:
        return not_implemented(context, GetCommitSignaturesResponse,
                               issue=24)  # pragma no cover

    def GetCommitMessages(self, request: GetCommitMessagesRequest,
                          context) -> GetCommitMessagesResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        results = {}
        for commit_id in request.commit_ids:
            commit_id = pycompat.sysbytes(commit_id)
            ctx = gitlab_revision_changeset(repo, commit_id)
            if ctx is None:
                # should not be an "internal" error, but
                # that's what Gitaly does anyway
                yield internal_error(
                    context, GetCommitMessagesResponse,
                    "failed to get commit message: object not found.",
                    log_level=logging.WARNING
                )
            results[commit_id] = ctx.description()
        for commit_id, msg in results.items():
            yield GetCommitMessagesResponse(commit_id=commit_id,
                                            message=msg)


def parse_find_commits_request_opts(request, repo):
    opts = {
        b'follow': request.follow,
        b'no_merges': request.skip_merges,
        b'limit': request.limit + request.offset,
    }
    # TODO: implement 'request.first_parent' option
    # khanchi97: found that its counterpart follow-first in "hg log" is
    # deprecated and give wrong results with other options like revision,
    # all, etc.
    if request.author:
        opts[b'user'] = [request.author]
    after = request.after.ToSeconds()
    before = request.before.ToSeconds()
    date = getdate(after, before)
    if date is not None:
        opts[b'date'] = date

    revision = request.revision
    if request.all:
        opts[b'rev'] = [b'0:tip']
    elif not revision:
        revision = get_default_gitlab_branch(repo)
    if revision and not request.all:
        # `revision` and `all` are mutually exclusive,
        # if both present `all` gets the precedence
        revset = revset_from_gitlab_revision(repo, revision)
        opts[b'rev'] = [revset]
    return opts


def getdate(after, before):
    if after and before:
        after = _isoformat_from_seconds(after)
        before = _isoformat_from_seconds(before)
        return "%s UTC to %s UTC" % (after, before)
    elif after:
        after = _isoformat_from_seconds(after)
        return ">%s UTC" % after
    elif before:
        before = _isoformat_from_seconds(before)
        return "<%s UTC" % before
    return None


def _isoformat_from_seconds(secs):
    ts = Timestamp()
    ts.FromSeconds(int(secs))
    dt = ts.ToDatetime()
    return dt.isoformat()


def revset_from_gitlab_revision(repo, revision):
    """Find mercurial revset from a given GitLab revision.

    In theory, a GitLab revision could be any Git valid revspec, that
    we'd had to translate into its Mercurial counterpart.

    At this point, we only support most common git revision ranges, and
    a single revision.

    :return: the corresponding mercurial `revset`, or ``None`` if not found.
    """
    if b'...' in revision:
        #
        # r1...r2
        #    In git revspec, this implies csets ancestors of r1 or r2,
        #    but not ancestors of both
        #
        rev_start, rev_end = revision.split(b'...')
        if not rev_start:
            ctx_start = gitlab_revision_changeset(repo, b'HEAD')
        else:
            ctx_start = gitlab_revision_changeset(repo, rev_start)
        if not rev_end:
            ctx_end = gitlab_revision_changeset(repo, b'HEAD')
        else:
            ctx_end = gitlab_revision_changeset(repo, rev_end)
        left = ctx_start.rev()
        right = ctx_end.rev()
        branchpoint = repo.revs(b"ancestor(%d, %d)" % (left, right)).first()
        revset = b"only(%d + %d, %d)" % (left, right, branchpoint)
        # sort them in descending order
        revset = b"sort(%s, -rev)" % revset
        return revset
    elif b'..' in revision:
        #
        # r1..r2
        #    In git revspec, this implies csets ancestors of r2, but not r1
        #
        # So the true Mercurial equivalent revset is actually `r2 % r1`.
        # Sadly, we happen to know `%` to be less efficient than DAG ranges.
        rev_start, rev_end = revision.split(b'..')
        if not rev_start:
            ctx_start = gitlab_revision_changeset(repo, b'HEAD')
        else:
            ctx_start = gitlab_revision_changeset(repo, rev_start)
        if not rev_end:
            ctx_end = gitlab_revision_changeset(repo, b'HEAD')
        else:
            ctx_end = gitlab_revision_changeset(repo, rev_end)
        revset = b"::%s - ::%s" % (ctx_end, ctx_start)
        # sort them in descending order
        revset = b"sort(%s, -rev)" % revset
        return revset
    else:
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None:
            return None
        revset = b"reverse(::%s)" % ctx
        return revset


def latest_changeset_for_path(path, seen_from):
    """Return latest ancestor of ``seen_from`` that touched the given path.

    :param bytes path: subdir or file
    :param seen_from: changectx
    """
    # gracinet: just hoping that performance wise, this does the right
    # thing, i.e do any scanning from the end
    # While we can be reasonably confident that the file exists
    # in the given revision, there are cases where deduplication implies
    # that the filelog() predicate would not see any new file revision
    # in some subgraph, because it's identical to another one that's not
    # in that subgraph. Hence using the slower `file` is the only way
    # to go.
    repo = seen_from.repo()
    rev = repo.revs('file(%s) and ::%s', b'path:' + path, seen_from).last()
    return None if rev is None else repo[rev]


def blamelines(repo, ctx, file):
    """Yield blame lines of a file.
    """
    fctx = ctx[file]
    for line_no, line in enumerate(fctx.annotate(), start=1):
        old_line_no = line.lineno
        # required blame line format that get parsed by Rails:
        #   '<hash_id> <old_line_no> <line_no>\n\t<line_text>'
        yield b'%s %d %d\n\t%s' % (line.fctx.hex(), old_line_no, line_no,
                                   line.text)
