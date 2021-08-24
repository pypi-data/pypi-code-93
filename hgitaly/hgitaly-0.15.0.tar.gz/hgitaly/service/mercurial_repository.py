# coding: utf-8
# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging

from mercurial import (
    pycompat,
)

from ..errors import (
    not_implemented,
)
from ..stub.mercurial_repository_pb2 import (
    ConfigItemType,
    GetConfigItemRequest,
    GetConfigItemResponse,
)
from ..stub.mercurial_repository_pb2_grpc import (
    MercurialRepositoryServiceServicer,
)
from ..servicer import HGitalyServicer

logger = logging.getLogger(__name__)


class MercurialRepositoryServicer(MercurialRepositoryServiceServicer,
                                  HGitalyServicer):
    """MercurialRepositoryService implementation.

    The ordering of methods in this source file is the same as in the proto
    file.
    """
    def GetConfigItem(self,
                      request: GetConfigItemRequest,
                      context) -> GetConfigItemResponse:
        repo = self.load_repo(request.repository, context)
        section = pycompat.sysbytes(request.section)
        name = pycompat.sysbytes(request.name)

        if request.as_type == ConfigItemType.BOOL:
            # TODO error treatment if value is not boolean
            return GetConfigItemResponse(
                as_bool=repo.ui.configbool(section, name))

        return not_implemented(  # pragma no cover
            context, GetConfigItemResponse,
            issue=60)
