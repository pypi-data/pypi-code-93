# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok_attachment.bloks.wkhtml2pdf.exceptions import PageValidityException
from sqlalchemy.exc import IntegrityError


class TestPage:

    @pytest.fixture(autouse=True, scope='function')
    def define_registry(self, rollback_registry):
        self.registry = rollback_registry

    def test_height(self):
        with pytest.raises(IntegrityError):
            self.registry.Attachment.WkHtml2Pdf.Page.insert(
                label='Test', height=-1, width=10)

    def test_width(self):
        with pytest.raises(IntegrityError):
            self.registry.Attachment.WkHtml2Pdf.Page.insert(
                label='Test', width=-1, height=10)

    def test_empty(self):
        with pytest.raises(PageValidityException):
            self.registry.Attachment.WkHtml2Pdf.Page.insert(
                label='Test')

    def test_size(self):
        self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')

    def test_size_first_than_height_and_width(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter', height=80, width=120)
        assert page.height is None
        assert page.width is None

    def test_height_and_width(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', height=80, width=120)
        assert page.height
        assert page.width

    def test_get_options_with_size(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        assert page.get_options() == ['--page-size', 'Letter']

    def test_get_options_with_width_and_height(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', width=120, height=80)
        assert page.get_options() == [
            '--page-width', '120', '--page-height', '80']
