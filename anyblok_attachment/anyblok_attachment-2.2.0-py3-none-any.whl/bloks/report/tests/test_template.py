# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok_attachment.bloks.report.exceptions import (
    RenderException, TemplateException, PathException)
from os import urandom


@pytest.mark.usefixtures('rollback_registry')
class TestTemplate:

    @pytest.fixture(autouse=True, scope='function')
    def define_registry(self, rollback_registry):
        self.registry = rollback_registry

    def test_without_render(self):
        template = self.registry.Attachment.Template.insert(
            name="test",
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        with pytest.raises(RenderException):
            template.render({})

    def test_check_if_file_must_be_generated_1(self):
        template = self.registry.Attachment.Template.insert(
            name="test",
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        document = self.registry.Attachment.Document.insert(
            template=template)
        assert template.check_if_file_must_be_generated(document)

    def test_check_if_file_must_be_generated_2(self):
        template = self.registry.Attachment.Template.insert(
            name="test",
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        document = self.registry.Attachment.Document.insert()
        assert not template.check_if_file_must_be_generated(document)

    def test_update_document(self):
        template = self.registry.Attachment.Template.insert(
            name="test",
            filename='test-{doc.uuid}-{doc.version}',
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        document = self.registry.Attachment.Document.insert(
            template=template)
        file_ = urandom(10)
        template.update_document(document, file_, {})
        attachment_postgres = self.registry.System.Blok.query().get(
            'attachment-postgres')
        if attachment_postgres.is_installed('attachment-postgres'):
            assert document.lobject == file_
        else:
            assert document.file == file_

        assert document.contenttype == 'plain/text'
        assert document.filesize == len(file_)
        filename = template.filename.format(doc=document)
        assert document.filename == filename

    def test_get_parser(self):
        template = self.registry.Attachment.Template.insert(
            name="test",
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        assert template.get_parser() is self.registry.Attachment.Parser

    def test_get_template(self):
        template = self.registry.Attachment.Template.insert(
            name="test",
            template_path='report#=#tests/template.tmpl',
            model="Model.Attachment.Template")
        assert template.get_template() == "template\n"

    def test_without_parser(self):
        with pytest.raises(TemplateException):
            self.registry.Attachment.Template.insert(
                name="test",
                template_path='report#=#tests/template.tmpl',
                parser_model='',
                model="Model.Attachment.Template")

    def test_without_template(self):
        with pytest.raises((TemplateException, PathException)):
            self.registry.Attachment.Template.insert(
                name="test",
                template_path='',
                model="Model.Attachment.Template")
