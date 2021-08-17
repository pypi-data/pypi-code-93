# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok_attachment.bloks.report.common import format_path
from anyblok_attachment.bloks.report.exceptions import PathException
from anyblok.blok import BlokManager
import os


@pytest.mark.usefixtures('rollback_registry')
class TestReportCommon:

    @pytest.fixture(autouse=True, scope='function')
    def define_registry(self, rollback_registry):
        self.registry = rollback_registry

    def get_absolute_path(self):
        return os.path.join(
            BlokManager.getPath('report'), 'tests', 'test_common.py')

    def test_format_path_without_module(self):
        assert format_path(self.get_absolute_path()) == self.get_absolute_path()

    def test_format_path_with_module(self):
        format_path_ = format_path('report#=#tests/test_common.py')
        assert format_path_ == self.get_absolute_path()

    def test_format_path_with_invalid_path(self):
        with pytest.raises(PathException):
            format_path('report#=#wrong/path')
