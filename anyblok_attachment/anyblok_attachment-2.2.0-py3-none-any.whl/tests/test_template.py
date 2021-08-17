# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest  # noqa
from anyblok_attachment.bloks.report.exceptions import (
    TemplateException, PathException)
from os import urandom


class TestTemplate:

    def test_without_parser(self, registry_report_1):
        with pytest.raises(TemplateException):
            registry_report_1.Attachment.Template.MyTemplate.insert(
                name="test",
                parser_model="",
                template_path="report#=#common.py",
                model="Model.System.Blok"
            )

    def test_without_template(self, registry_report_1):
        with pytest.raises(PathException):
            registry_report_1.Attachment.Template.MyTemplate.insert(
                name="test",
                template_path="",
                model="Model.System.Blok"
            )

    def test_add_new_parser_type_single_table(self, registry_report_1):
        file_ = urandom(10)
        registry_report_1.Attachment.Template.MyTemplate.file_ = file_
        template = registry_report_1.Attachment.Template.MyTemplate.insert(
            name="test",
            template_path="report#=#common.py",
            filename='test',
            model="Model.System.Blok"
        )
        document = registry_report_1.Attachment.Document.insert(
            template=template)
        get_file = document.get_file()
        wanted_file = {
            'filename': 'test',
            'file': file_,
            'filesize': len(file_),
            'contenttype': 'plain/text',
            'file_added_at': get_file['file_added_at'],
            'hash': get_file['hash']
        }
        assert get_file == wanted_file
        assert get_file['hash']
        assert get_file['file_added_at']

    def test_add_new_parser_type_multi_table(self, registry_report_2):
        file_ = urandom(10)
        registry_report_2.Attachment.Template.MyTemplate.file_ = file_
        template = registry_report_2.Attachment.Template.MyTemplate.insert(
            name="test",
            template_path="report#=#common.py",
            filename='test',
            model="Model.System.Blok"
        )
        document = registry_report_2.Attachment.Document.insert(
            template=template)
        get_file = document.get_file()
        wanted_file = {
            'filename': 'test',
            'file': file_,
            'filesize': len(file_),
            'contenttype': 'plain/text',
            'file_added_at': get_file['file_added_at'],
            'hash': get_file['hash']
        }
        assert get_file == wanted_file
        assert get_file['hash']
        assert get_file['file_added_at']

    def test_add_template_with_wkhtml2pdf(self, registry_report_3):
        file_ = urandom(10)
        registry_report_3.Attachment.Template.MyTemplate.file_ = file_
        page = registry_report_3.Attachment.WkHtml2Pdf.Page.insert(
            label="A4", size="A4")
        wkhtml2pdf = registry_report_3.Attachment.WkHtml2Pdf.insert(
            label="Custom", page=page)
        template = registry_report_3.Attachment.Template.MyTemplate.insert(
            name="test",
            template_path="report#=#common.py",
            filename='test',
            model="Model.System.Blok",
            wkhtml2pdf_configuration=wkhtml2pdf
        )
        document = registry_report_3.Attachment.Document.insert(
            template=template)
        get_file = document.get_file()
        assert get_file['file']
        assert get_file['hash']
        assert get_file['file_added_at']

    def test_add_template_with_wkhtml2pdf_test_conf_changed(self,
                                                            registry_report_3):
        file_ = urandom(10)
        registry_report_3.Attachment.Template.MyTemplate.file_ = file_
        page = registry_report_3.Attachment.WkHtml2Pdf.Page.insert(
            label="A4", size="A4")
        page.refresh()
        wkhtml2pdf = registry_report_3.Attachment.WkHtml2Pdf.insert(
            label="Custom", page=page)
        wkhtml2pdf.refresh()
        template = registry_report_3.Attachment.Template.MyTemplate.insert(
            name="test",
            template_path="report#=#common.py",
            filename='test',
            model="Model.System.Blok",
            wkhtml2pdf_configuration=wkhtml2pdf
        )
        template.refresh()
        document = registry_report_3.Attachment.Document.insert(
            template=template)
        document.get_file()
        assert not template.check_if_file_must_be_generated(document)
        wkhtml2pdf.margin_top = 20
        registry_report_3.flush()
        assert template.check_if_file_must_be_generated(document)

    def test_add_template_with_wkhtml2pdf_test_page_conf_changed(
        self, registry_report_3
    ):
        file_ = urandom(10)
        registry_report_3.Attachment.Template.MyTemplate.file_ = file_
        page = registry_report_3.Attachment.WkHtml2Pdf.Page.insert(
            label="A4", size="A4")
        page.refresh()
        wkhtml2pdf = registry_report_3.Attachment.WkHtml2Pdf.insert(
            label="Custom", page=page)
        wkhtml2pdf.refresh()
        template = registry_report_3.Attachment.Template.MyTemplate.insert(
            name="test",
            template_path="report#=#common.py",
            filename='test',
            model="Model.System.Blok",
            wkhtml2pdf_configuration=wkhtml2pdf
        )
        template.refresh()
        document = registry_report_3.Attachment.Document.insert(
            template=template)
        document.get_file()
        assert not template.check_if_file_must_be_generated(document)
        page.size = "A3"
        registry_report_3.flush()
        assert template.check_if_file_must_be_generated(document)
