# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok_mixins.mixins.exceptions import ForbidDeleteException
from ..exceptions import ProtectedFieldException, NoFileException
from os import urandom


@pytest.mark.usefixtures('rollback_registry')
class TestLatest:

    @pytest.fixture(autouse=True, scope='function')
    def define_registry(self, rollback_registry):
        self.registry = rollback_registry

    def test_insert_from_document(self):
        document = self.registry.Attachment.Document.insert()
        assert document.type == 'latest'

    def test_insert_from_latest(self):
        document = self.registry.Attachment.Document.Latest.insert()
        assert document.type == 'latest'

    def test_same_version_for_two_different_document(self):
        document1 = self.registry.Attachment.Document.Latest.insert()
        document2 = self.registry.Attachment.Document.Latest.insert()
        assert document1.version == document2.version
        assert document1.uuid != document2.uuid

    def test_query_only_latest(self):
        document = self.registry.Attachment.Document.Latest.insert()
        self.registry.Attachment.Document.History.insert(uuid=document.uuid,
                                                         version_number=100000)
        assert self.registry.Attachment.Document.Latest.query().filter_by(
            uuid=document.uuid).one() is document

    def test_create_an_history_without_file(self):
        document = self.registry.Attachment.Document.insert()
        with pytest.raises(NoFileException):
            document.historize_a_copy()

    def test_create_an_history_with_file(self):
        file_ = urandom(100)
        document = self.registry.Attachment.Document.insert(file=file_)
        version = document.version
        assert document.has_file()
        document.historize_a_copy()
        assert document.version != version
        assert document.previous_version.next_version is document
        assert document.has_file()
        assert document.previous_version.has_file()

    def test_udpate_without_file(self):
        document = self.registry.Attachment.Document.insert()
        version = document.version
        document.data = {'other': 'data'}
        self.registry.flush()
        assert document.version == version
        assert document.previous_version is None

    def test_update_with_file(self):
        file_ = urandom(100)
        document = self.registry.Attachment.Document.insert(file=file_)
        version = document.version
        assert document.has_file()
        document.data = {'other': 'data'}
        self.registry.flush()
        assert document.version != version
        assert document.previous_version.next_version is document
        assert not document.has_file()
        assert document.previous_version.has_file()

    def test_delete(self):
        document = self.registry.Attachment.Document.insert()
        with pytest.raises(ForbidDeleteException):
            document.delete()
            self.registry.flush()

    def test_versions(self):
        file_ = urandom(100)
        document = self.registry.Attachment.Document.insert(file=file_)
        document.historize_a_copy()
        assert document.previous_versions == [document.previous_version]

    def test_update_protected_fields(self):
        document = self.registry.Attachment.Document.insert()
        with pytest.raises(ProtectedFieldException):
            document.version_number = 1000000000
            self.registry.flush()

    def test_add_new_version_without_file(self):
        document = self.registry.Attachment.Document.insert()
        with pytest.raises(NoFileException):
            document.add_new_version()

    def test_add_new_version_with_file(self):
        file_ = urandom(100)
        document = self.registry.Attachment.Document.insert(file=file_)
        version = document.version
        assert document.has_file()
        document.add_new_version()
        assert document.version != version
        assert document.previous_version.next_version is document
        assert not document.has_file()
        assert document.previous_version.has_file()
