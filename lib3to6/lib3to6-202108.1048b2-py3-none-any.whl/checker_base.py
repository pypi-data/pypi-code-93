# This file is part of the lib3to6 project
# https://github.com/mbarkhau/lib3to6
#
# Copyright (c) 2019-2021 Manuel Barkhau (mbarkhau@gmail.com) - MIT License
# SPDX-License-Identifier: MIT
from __future__ import generator_stop
import ast
from . import common


class CheckerBase:
    version_info: common.VersionInfo = common.VersionInfo()

    def __call__(self, ctx: common.BuildContext, tree: ast.Module) ->None:
        raise NotImplementedError()
