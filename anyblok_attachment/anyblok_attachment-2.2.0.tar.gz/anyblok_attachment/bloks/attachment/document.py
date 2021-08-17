# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from anyblok.column import (
    UUID, String, DateTime, Json, Integer, LargeBinary, Selection
)
from anyblok.field import Function
from datetime import datetime
from sqlalchemy import insert, select
from sqlalchemy.orm.session import object_state
from anyblok.common import anyblok_column_prefix
from uuid import uuid1
from .exceptions import (
    NoFileException, ProtectedFieldException
)


register = Declarations.register
Attachment = Declarations.Model.Attachment
Mixin = Declarations.Mixin


@register(Attachment)
class Document:
    DOCUMENT_TYPE = None

    uuid = UUID(primary_key=True, binary=False, nullable=False)
    version_number = Integer(primary_key=True, nullable=False)
    version = Function(fget="get_version")

    created_at = DateTime(default=datetime.now, nullable=False)
    historied_at = DateTime()

    data = Json(default=dict)

    file_added_at = DateTime()
    filename = String(size=256)
    contenttype = String()
    filesize = Integer()
    file = LargeBinary()
    hash = String(size=256)

    type = Selection(selections={'latest': 'Latest', 'history': 'History'},
                     nullable=False)

    previous_doc_uuid = UUID()
    previous_doc_version_number = Integer()
    previous_version = Function(fget="get_previous_version")
    next_version = Function(fget="get_next_version")
    previous_versions = Function(fget="get_previous_versions")

    @classmethod
    def get_file_fields(cls):
        return ['file', 'file_added_at', 'contenttype', 'filename', 'hash',
                'filesize']

    def get_file(self):
        return self.to_dict(*self.get_file_fields())

    def set_file(self, file_):
        self.file = file_

    def get_version(self):
        return "V-%06d" % self.version_number

    def get_previous_version(self):
        Doc = self.anyblok.Attachment.Document
        query = Doc.query()
        query = query.filter(Doc.uuid == self.previous_doc_uuid)
        query = query.filter(
            Doc.version_number == self.previous_doc_version_number)
        return query.one_or_none()

    def get_next_version(self):
        Doc = self.anyblok.Attachment.Document
        query = Doc.query()
        query = query.filter(Doc.previous_doc_uuid == self.uuid)
        query = query.filter(
            Doc.previous_doc_version_number == self.version_number)
        return query.one_or_none()

    def get_previous_versions(self):
        res = []
        current = self
        while current.previous_version:
            current = current.previous_version
            res.append(current)

        return res

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Document, cls).define_mapper_args()
        if cls.__registry_name__ == 'Model.Attachment.Document':
            mapper_args.update({'polymorphic_on': cls.type})

        mapper_args.update({'polymorphic_identity': cls.DOCUMENT_TYPE})
        return mapper_args

    @classmethod
    def insert(cls, *args, **kwargs):
        if cls.__registry_name__ == 'Model.Attachment.Document':
            return cls.anyblok.Attachment.Document.Latest.insert(
                *args, **kwargs)

        return super(Document, cls).insert(*args, **kwargs)

    @classmethod
    def query(cls, *args, **kwargs):
        query = super(Document, cls).query(*args, **kwargs)
        if cls.__registry_name__ != 'Model.Attachment.Document':
            query = query.filter(cls.type == cls.DOCUMENT_TYPE)

        return query

    def has_file(self):
        if self.file:
            return True

        return False

    @classmethod
    def filter_has_not_file(cls):
        return cls.file == None  # noqa


@register(Attachment.Document, tablename=Attachment.Document)
class Latest(Attachment.Document, Mixin.ForbidDelete):
    DOCUMENT_TYPE = 'latest'

    @classmethod
    def insert(cls, *args, **kwargs):
        uuid = uuid1()
        values = kwargs.copy()
        values.update(dict(uuid=uuid, version_number=1))
        return super(Latest, cls).insert(*args, **values)

    def get_modified_fields(self):
        state = object_state(self)
        modified_fields = []
        for attr in state.manager.attributes:
            if not hasattr(attr.impl, 'get_history'):
                continue

            added, unmodified, deleted = attr.impl.get_history(
                state, state.dict)

            if added or deleted:
                field = attr.key
                if field.startswith(anyblok_column_prefix):
                    field = field[len(anyblok_column_prefix):]

                modified_fields.append(field)

        return modified_fields

    @classmethod
    def get_forbidden_modify_fields(cls):
        return ['uuid', 'version_number', 'creates_at',
                'attachment_document_uuid', 'attachment_document_version']

    def is_unmodified_file(self, modified_fields):
        if 'file' not in modified_fields or self.file is None:
            return True

        return False

    def put_to_none(self, field):
        setattr(self, field, None)

    @classmethod
    def before_update_orm_event(cls, mapper, connection, target):
        modified_fields = target.get_modified_fields()
        forbidden_fields = set(cls.get_forbidden_modify_fields())
        inter = set.intersection(forbidden_fields, set(modified_fields))
        if inter:
            raise ProtectedFieldException(
                "Protected fields %s, they can't be modified",
                list(inter)
            )

        Q = cls.query().filter(cls.uuid == target.uuid)
        Q = Q.filter(cls.version_number == target.version_number)
        Q = Q.filter(cls.filter_has_not_file())
        if Q.count():
            # No file in DB, then no archive is need
            return

        old_version_number = target.version_number
        new_version_number = old_version_number + 1

        Column = cls.anyblok.System.Column
        columns = Column.query().filter(
            Column.model == 'Model.Attachment.Document')
        columns = columns.all().name
        new_vals = {x: getattr(target, x) for x in columns}

        target.version_number = new_version_number
        target.created_at = datetime.now()
        target.previous_doc_uuid = target.uuid
        target.previous_doc_version_number = old_version_number

        if target.type != 'latest':
            target.type = 'latest'

        if modified_fields == ['type']:
            pass  # do nothing on files
        elif target.is_unmodified_file(modified_fields):
            for field in target.get_file_fields():
                target.put_to_none(field)

        new_vals.update(target.update_copied_value(
            modified_fields, old_version_number))
        new_vals['type'] = 'history'
        target.new_history = new_vals

    def update_copied_value(self, modified_fields, old_version_number):
        document = self.anyblok.Attachment.Document.__table__
        query = select([getattr(document.c, field)
                        for field in modified_fields])
        query = query.where(document.c.uuid == self.uuid)
        query = query.where(document.c.version_number == old_version_number)
        res = self.anyblok.session.connection().execute(query)

        vals = res.fetchone()
        return {x: vals[x] for x in modified_fields}

    @classmethod
    def after_update_orm_event(cls, mapper, connection, target):
        if hasattr(target, 'new_history') and target.new_history:
            conn = cls.anyblok.session
            conn.execute(
                insert(
                    cls.anyblok.Attachment.Document.History.__table__
                ).values(**target.new_history)
            )
            delattr(target, 'new_history')

    def historize_a_copy(self):
        if not self.has_file():
            raise NoFileException(
                "Can not archive %s, because the document have not got file"
            )

        self.anyblok.flush()  # the file must be send to exist on db
        self.type = 'history'
        self.anyblok.flush()  # flush call the listen then do the archive

    def add_new_version(self):
        if not self.has_file():
            raise NoFileException(
                "Can not archive %s, because the document have not got file")

        for field in self.get_file_fields():
            setattr(self, field, None)

        self.anyblok.flush()  # flush call the listen then do the archive


@register(Attachment.Document, tablename=Attachment.Document)
class History(Attachment.Document, Mixin.ReadOnly):
    DOCUMENT_TYPE = 'history'
