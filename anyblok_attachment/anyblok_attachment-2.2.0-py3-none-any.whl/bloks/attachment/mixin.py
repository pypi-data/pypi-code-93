# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.declarations import hybrid_method
from anyblok.column import UUID, Integer
from anyblok.field import Function
from .exceptions import NoneValueException, NotLatestException


@Declarations.register(Declarations.Mixin)
class LatestDocument:

    latest_document_uuid = UUID()
    latest_document = Function(fget='get_latest_document',
                               fset='set_latest_document',
                               fdel='del_latest_document')

    def get_latest_document(self):
        Document = self.anyblok.Attachment.Document.Latest
        query = Document.query()
        query = query.filter(
            Document.uuid == self.latest_document_uuid
        )
        return query.one_or_none()

    def set_latest_document(self, document):
        if document.uuid is None:
            raise NoneValueException("Uuid value is None")

        if document.type != 'latest':
            raise NotLatestException(
                "You try to set a versioned document, this action is "
                "forbidden"
            )

        self.latest_document_uuid = document.uuid

    def del_latest_document(self):
        self.latest_document_uuid = None

    @hybrid_method
    def is_latest_document(self, document):
        if document.type != 'latest':
            raise NotLatestException(
                "You try to compare the latest document with a versioned "
                "document, this action is forbidden"
            )

        return self.latest_document_uuid == document.uuid


@Declarations.register(Declarations.Mixin)
class VersionedDocument:

    versioned_document_uuid = UUID()
    versioned_document_version_number = Integer()
    versioned_document = Function(fget='get_versioned_document',
                                  fset='set_versioned_document',
                                  fdel='del_versioned_document')

    def get_versioned_document(self):
        Document = self.anyblok.Attachment.Document
        query = Document.query()
        query = query.filter(
            Document.uuid == self.versioned_document_uuid,
            Document.version_number == self.versioned_document_version_number
        )
        return query.one_or_none()

    def set_versioned_document(self, document):
        if document.uuid is None:
            raise NoneValueException("Uuid value is None")

        self.versioned_document_uuid = document.uuid
        self.versioned_document_version_number = document.version_number

    def del_versioned_document(self):
        self.versioned_document_uuid = None
        self.versioned_document_version_number = None

    @hybrid_method
    def is_versioned_document(self, document):
        return (
            self.versioned_document_uuid == document.uuid and
            self.versioned_document_version_number == document.version_number)
