# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import gc
import logging
import os
import threading
import time
import weakref

from grpc import StatusCode
from mercurial import (
    error,
    hg,
    ui as uimod,
)
from mercurial.repoview import _filteredrepotypes
from .stub.shared_pb2 import (
    Repository,
)

GARBAGE_COLLECTING_RATE = 1000

logger = logging.getLogger(__name__)


def clear_repo_class(repo_class):
    _filteredrepotypes.pop(repo_class, None)


class HGitalyServicer:
    """Common features of all HGitaly services.

    Attributes:

    - :attr:`storages`: a :class:`dict` mapping storage names to corresponding
      root directory absolute paths, which are given as bytes since we'll have
      to convert paths to bytes anyway, which is the only promise a filesystem
      can make, and what Mercurial expects.
    - :attr:`ui`: base :class:`mercurial.ui.ui` instance from which repository
      uis are derived. In particular, it bears the common configuration.
    """

    repos_counter = threading.local()

    def __init__(self, storages):
        self.storages = storages
        self.ui = uimod.ui.load()

    def load_repo(self, repository: Repository, context):
        """Load the repository from storage name and relative path

        :param repository: Repository Gitaly Message, encoding storage name
            and relative path
        :param context: gRPC context (used in error raising)
        :raises: ``KeyError('storage', storage_name)`` if storage is not found.

        Error treatment: the caller doesn't have to do anything specific,
        the status code and the details are already set in context, and these
        are automatically propagated to the client (see corresponding test
        in `test_servicer.py`). Still, the caller can still catch the
        raised exception and change the code and details as they wish.
        """
        counter = self.repos_counter
        if getattr(counter, 'v', None) is None:
            counter.v = 0
        if counter.v % GARBAGE_COLLECTING_RATE == 0:
            logger.info("A total of %d repository objects have been "
                        "instantiated in this thread since startup. "
                        "Garbage collecting.", counter.v)
            start = time.time()
            gc_result = gc.collect()
            logger.info("Garbage collection done in %f seconds "
                        "(%d unreachable objects). Current GC stats: %r",
                        time.time() - start, gc_result, gc.get_stats())

        counter.v += 1

        # shamelessly taken from heptapod.wsgi for the Hgitaly bootstrap
        # note that Gitaly Repository has more than just a relative path,
        # we'll have to decide what we make of the extra information
        repo_path = self.repo_disk_path(repository, context)
        logger.info("loading repo at %r", repo_path)

        try:
            repo = hg.repository(self.ui, repo_path)
        except error.RepoError as exc:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(repr(exc.args))
            raise KeyError('repo', repo_path)
        weakref.finalize(repo, clear_repo_class, repo.unfiltered().__class__)
        srcrepo = hg.sharedreposource(repo)
        if srcrepo is not None:
            weakref.finalize(srcrepo, clear_repo_class,
                             srcrepo.unfiltered().__class__)

        return repo

    def repo_disk_path(self, repository: Repository, context):
        rpath = repository.relative_path
        if rpath.endswith('.git'):
            rpath = rpath[:-4] + '.hg'

        root_dir = self.storages.get(repository.storage_name)
        if root_dir is None:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(
                "No storage named %r" % repository.storage_name)
            raise KeyError('storage', repository.storage_name)

        # GitLab filesystem paths are always ASCII
        repo_path = os.path.join(root_dir, rpath.encode('ascii'))
        return repo_path
