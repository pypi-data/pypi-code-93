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


class TestHistorization:

    def test_get_versioned_document(self, registry_report_4):
        registry = registry_report_4
        file_ = urandom(100)
        doc = registry.Attachment.Document.insert(file=file_)
        t = registry.DocumentTest2.insert(versioned_document=doc)
        assert doc.version == t.versioned_document.version
        doc.historize_a_copy()
        assert doc.version != t.versioned_document.version

    def test_del_versioned_document(self, registry_report_4):
        registry = registry_report_4
        doc = registry.Attachment.Document.insert()
        t = registry.DocumentTest2.insert(versioned_document=doc)
        del t.versioned_document
        assert t.versioned_document_uuid is None
        assert t.versioned_document_version_number is None
        assert t.versioned_document is None

    def test_check_versioned_document(self, registry_report_4):
        registry = registry_report_4
        doc1 = registry.Attachment.Document.insert()
        registry.DocumentTest2.insert(versioned_document=doc1)
        doc2 = registry.Attachment.Document.insert()
        t2 = registry.DocumentTest2.insert(versioned_document=doc2)
        query = registry.DocumentTest2.query()
        query = query.filter(registry.DocumentTest2.is_versioned_document(doc2))
        assert query.one() is t2
