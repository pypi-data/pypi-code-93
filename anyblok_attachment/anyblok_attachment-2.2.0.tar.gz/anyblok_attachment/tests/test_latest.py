# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest  # noqa
from os import urandom
from anyblok_attachment.bloks.attachment.exceptions import NotLatestException


class TestLatestDocument:

    def test_get_latest_document(self, registry_report_4):
        registry = registry_report_4
        file_ = urandom(100)
        doc = registry.Attachment.Document.insert(file=file_)
        t = registry.DocumentTest.insert()
        t.latest_document = doc
        assert t.latest_document.uuid == doc.uuid
        assert t.latest_document.version == doc.version
        doc.historize_a_copy()
        assert t.latest_document.uuid == doc.uuid
        assert t.latest_document.version == doc.version

    def test_del_latest_document(self, registry_report_4):
        registry = registry_report_4
        doc = registry.Attachment.Document.insert()
        t = registry.DocumentTest.insert(latest_document=doc)
        del t.latest_document
        assert t.latest_document_uuid is None
        assert t.latest_document is None

    def test_check_latest_document(self, registry_report_4):
        registry = registry_report_4
        doc1 = registry.Attachment.Document.insert()
        registry.DocumentTest.insert(latest_document=doc1)
        doc2 = registry.Attachment.Document.insert()
        t2 = registry.DocumentTest.insert(latest_document=doc2)
        query = registry.DocumentTest.query()
        query = query.filter(registry.DocumentTest.is_latest_document(doc2))
        assert query.one() is t2

    def test_set_latest_document_with_versionned_document(self,
                                                          registry_report_4):
        registry = registry_report_4
        file_ = urandom(100)
        doc = registry.Attachment.Document.insert(file=file_)
        t = registry.DocumentTest.insert()
        doc.historize_a_copy()
        with pytest.raises(NotLatestException):
            t.latest_document = doc.previous_version

    def test_check_latest_document_with_versioned_document(self,
                                                           registry_report_4):
        registry = registry_report_4
        file_ = urandom(100)
        doc = registry.Attachment.Document.insert(file=file_)
        registry.DocumentTest.insert(latest_document=doc)
        doc.historize_a_copy()
        query = registry.DocumentTest.query()
        with pytest.raises(NotLatestException):
            query = query.filter(registry.DocumentTest.is_latest_document(
                doc.previous_version))
