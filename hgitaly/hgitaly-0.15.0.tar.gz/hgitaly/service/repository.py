# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from grpc import StatusCode
import logging
import tempfile

from mercurial import (
    archival,
    scmutil,
    hg,
    vfs as vfsmod,
)

from heptapod.gitlab.branch import gitlab_branch_from_ref
from hgext3rd.heptapod.branch import set_default_gitlab_branch
from hgext3rd.heptapod.special_ref import write_gitlab_special_ref
from hgext3rd.heptapod.keep_around import (
    create_keep_around,
    parse_keep_around_ref,
)

from ..errors import (
    internal_error,
    invalid_argument,
    not_implemented,
)
from ..branch import (
    iter_gitlab_branches,
)
from ..gitlab_ref import (
    parse_special_ref,
    ensure_special_refs,
)
from ..revision import (
    CHANGESET_HASH_BYTES_REGEXP,
    gitlab_revision_changeset,
)
from ..stub.repository_service_pb2 import (
    CreateRepositoryRequest,
    CreateRepositoryResponse,
    FindMergeBaseRequest,
    FindMergeBaseResponse,
    RepositoryExistsRequest,
    RepositoryExistsResponse,
    GetArchiveRequest,
    GetArchiveResponse,
    HasLocalBranchesRequest,
    HasLocalBranchesResponse,
    WriteRefRequest,
    WriteRefResponse,
    ApplyGitattributesRequest,
    ApplyGitattributesResponse,
)
from ..stub.repository_service_pb2_grpc import RepositoryServiceServicer
from ..servicer import HGitalyServicer
from ..stream import WRITE_BUFFER_SIZE
from ..path import (
    InvalidPath,
    validate_relative_path,
)
from .. import message


logger = logging.getLogger(__name__)
DEFAULT_BRANCH_FILE_NAME = b'default_gitlab_branch'
ARCHIVE_FORMATS = {
    GetArchiveRequest.Format.Value('ZIP'): b'zip',
    GetArchiveRequest.Format.Value('TAR'): b'tar',
    GetArchiveRequest.Format.Value('TAR_GZ'): b'tgz',
    GetArchiveRequest.Format.Value('TAR_BZ2'): b'tbz2',
}


class RepositoryServicer(RepositoryServiceServicer, HGitalyServicer):
    """RepositoryServiceService implementation.
    """

    def FindMergeBase(self,
                      request: FindMergeBaseRequest,
                      context) -> FindMergeBaseResponse:
        logger.debug("FindMergeBase request=%r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        if len(request.revisions) < 2:
            # require at least 2 revisions
            return invalid_argument(
                context, FindMergeBaseResponse,
                'FindMergeBase: at least 2 revisions are required'
            )
        ctxs = []
        for rev in request.revisions:
            ctx = gitlab_revision_changeset(repo, rev)
            if ctx is None:
                return FindMergeBaseResponse()
            ctxs.append(ctx)
        # As per Gitaly, In future we may support this method for more
        # than two revisions, but for now we don't.
        ctx_from, ctx_to = ctxs[0], ctxs[1]
        gca = repo.revs(
            b"ancestor(%d, %d)" % (ctx_from.rev(), ctx_to.rev())
        ).first()
        base = repo[gca].hex() if gca is not None else ''
        return FindMergeBaseResponse(base=base)

    def RepositoryExists(self,
                         request: RepositoryExistsRequest,
                         context) -> RepositoryExistsResponse:
        try:
            self.load_repo(request.repository, context)
            exists = True
        except KeyError:
            exists = False
            # TODO would be better to have a two-layer helper
            # in servicer: load_repo() for proper gRPC error handling and
            # load_repo_raw_exceptions() (name to be improved) to get the
            # raw exceptions
            context.set_code(StatusCode.OK)
            context.set_details('')

        return RepositoryExistsResponse(exists=exists)

    def GetArchive(self,
                   request: GetArchiveRequest,
                   context) -> GetArchiveResponse:
        logger.debug("GetArchive request=%r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        ctx = repo[request.commit_id]

        patterns = []
        path = request.path
        if path:
            try:
                path = validate_relative_path(repo, path)
            except InvalidPath:
                return invalid_argument(context, GetArchiveResponse,
                                        "Invalid path: '%s'" % path)
            patterns.append(b"path:" + path)

        match = scmutil.match(ctx, pats=patterns, opts={})

        # using an anonymous (not linked) temporary file
        # TODO OPTIM check if archive is not by any chance
        # using a tempfile already…
        with tempfile.TemporaryFile(
                mode='wb+',  # the default, but let's insist on binary here
                buffering=WRITE_BUFFER_SIZE) as tmpf:
            archival.archive(
                repo,
                tmpf,
                ctx.node(),
                ARCHIVE_FORMATS[request.format],
                True,  # decode (TODO this is the default but what is this?)
                match,
                request.prefix.encode(),
                subrepos=False  # maybe later, check what GitLab's standard is
            )

            tmpf.seek(0)
            while True:
                data = tmpf.read(WRITE_BUFFER_SIZE)
                if not data:
                    break
                yield GetArchiveResponse(data=data)

    def HasLocalBranches(self,
                         request: HasLocalBranchesRequest,
                         context) -> HasLocalBranchesResponse:
        repo = self.load_repo(request.repository, context)
        # the iteration should stop as soon at first branchmap entry which
        # has a non closed head (but all heads in that entry would be checked
        # to be non closed)
        return HasLocalBranchesResponse(value=any(iter_gitlab_branches(repo)))

    def WriteRef(
            self,
            request: WriteRefRequest,
            context) -> WriteRefResponse:
        """Create or update a GitLab ref.

        The reference Gitaly implementation treats two cases, ``HEAD`` being
        the only supported symbolic ref. Excerpt as of GitLab 13.9.0::

          func (s *server) writeRef(ctx context.Context,
                                    req *gitalypb.WriteRefRequest) error {
            if string(req.Ref) == "HEAD" {
              return s.updateSymbolicRef(ctx, req)
            }
            return updateRef(ctx, s.cfg, s.gitCmdFactory, req)
          }

        On the other hand, the target revision is fully resolved, even
        when setting a non-symbolic ref.
        """
        ref, target = request.ref, request.revision
        repo = self.load_repo(request.repository, context)

        try:
            special_ref_name = parse_special_ref(ref)
            if special_ref_name is not None:
                target_sha = gitlab_revision_changeset(repo, target)
                ensure_special_refs(repo)
                write_gitlab_special_ref(repo, special_ref_name, target_sha)
                return WriteRefResponse()

            keep_around = parse_keep_around_ref(ref)
            if keep_around is not None:
                if (CHANGESET_HASH_BYTES_REGEXP.match(keep_around) is None
                        or target != keep_around):
                    return invalid_argument(
                        context, WriteRefResponse,
                        "Invalid target %r for keep-around %r. Only full "
                        "changeset ids in hexadecimal form are accepted and "
                        "target must "
                        "match the ref name" % (target, ref)
                    )
                create_keep_around(repo, target)
                return WriteRefResponse()
        except Exception:
            logger.exception(
                "WriteRef failed for Repository %r on storage %r",
                request.repository.relative_path,
                request.repository.storage_name)
            return WriteRefResponse()

        if ref != b'HEAD':
            return invalid_argument(
                context, WriteRefResponse,
                "Setting ref %r is not implemented in Mercurial (target %r) "
                "Does not make sense in the case of branches and tags, "
                "except maybe for bookmarks." % (ref, target))

        target_branch = gitlab_branch_from_ref(target)
        if target_branch is None:
            return invalid_argument(
                context, WriteRefResponse,
                "The default GitLab branch can only be set "
                "to a branch ref, got %r" % target)
        set_default_gitlab_branch(repo, target_branch)
        return WriteRefResponse()

    def ApplyGitattributes(self, request: ApplyGitattributesRequest,
                           context) -> ApplyGitattributesResponse:
        """Method used as testing bed for the `not_implemented` helper.

        It is unlikely we ever implement this one, and if we do something
        similar, we'll probably end up defining a ApplyHgAttributes anyway.
        """
        return not_implemented(context, ApplyGitattributesResponse,
                               issue=1234567)

    def CreateRepository(self, request: CreateRepositoryRequest,
                         context) -> CreateRepositoryResponse:
        try:
            repo_path = self.repo_disk_path(request.repository, context)
        except KeyError:
            storage_name = request.repository.storage_name
            msg = (
                'locate repository: no such storage: "%s"' % storage_name
            )
            return invalid_argument(context, CreateRepositoryResponse,
                                    message=msg)
        try:
            # check if already an Hg repository (logic similar to upstream Hg)
            wdir_vfs = vfsmod.vfs(repo_path, expandpath=True, realpath=True)
            hgvfs = vfsmod.vfs(wdir_vfs.join(b'.hg'))
            if hgvfs.exists():
                # To match with Gitaly/Git behavior, if repository already
                # initialized we should not return any error
                # (although `hg init` would throw an error)
                return CreateRepositoryResponse()
            hg.peer(self.ui, opts={}, path=repo_path, create=True)
        except Exception as exc:
            msg = (
                'create directories: "%s": error: %s'
            ) % (repo_path, repr(exc.args))
            return internal_error(context, CreateRepositoryResponse,
                                  message=msg)
        return CreateRepositoryResponse()
