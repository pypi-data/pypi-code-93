# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from uuid import uuid1
from anyblok.column import UUID, DateTime, String, Selection
from datetime import datetime
from .exceptions import TemplateException, RenderException, PathException
from .common import format_path
import os
import hashlib


Model = Declarations.Model
Attachment = Model.Attachment
register = Declarations.register


@register(Attachment)
class Template:
    """Base Model template to define the main configuration between templating
    system"""
    TYPE = 'invalid'

    uuid = UUID(primary_key=True, nullable=False, default=uuid1, binary=False)
    name = String(nullable=False)

    created_at = DateTime(nullable=False, default=datetime.now)
    updated_at = DateTime(nullable=False, default=datetime.now,
                          auto_update=True)

    model = String(foreign_key=Model.System.Model.use('name'), nullable=False,
                   size=256)
    filename = String(nullable=False,
                      default="{doc.uuid}-{doc.version}-{date}")
    type = Selection(selections="get_template_type", nullable=False)

    @classmethod
    def get_template_type(cls):
        """Give the tempate type"""
        return {
            'invalid': 'Invalid template'
        }

    template_from = Selection(selections="get_template_from", nullable=False,
                              default='path')
    template_path = String()

    @classmethod
    def get_template_from(cls):
        """Give the location of the template"""
        return {
            'path': 'From path on file system',
        }

    parser_from = Selection(selections="get_parser_from", nullable=False,
                            default='model')
    parser_model = String(default="Model.Attachment.Parser")

    @classmethod
    def get_parser_from(cls):
        """Give the location of the parser"""
        return {
            'model': 'From model',
        }

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Template, cls).define_mapper_args()
        if cls.__registry_name__ == 'Model.Attachment.Template':
            mapper_args.update({
                'polymorphic_identity': cls.TYPE,
                'polymorphic_on': cls.type,
            })
        else:
            mapper_args.update({
                'polymorphic_identity': cls.TYPE,
            })

        return mapper_args

    def get_template(self):
        """return the template file to compute"""
        if self.template_from == 'path':
            if not self.template_path:
                raise PathException("No path define for %r", self)

            path = format_path(self.template_path)
            if not os.path.isfile(path):
                raise PathException("%r must be a file", self.template_path)

            with open(path, 'r', encoding='utf-8') as fd:
                return fd.read()

    def get_parser(self):
        """return the template file to compute"""
        if self.parser_from == 'model':
            if self.parser_model:
                return self.anyblok.get(self.parser_model)

    def render(self, data):
        """Return the file create by the templating engine

        :param data: the serialized data
        """
        raise RenderException("No render defined by %r", self.__class__)

    def update_document(self, document, file_, data):
        """Update the document to fill file and content

        :param document: attachment document instance
        :param file_: bytes file
        :param data: serialized data
        """
        if document.has_file():
            document.add_new_version()

        document.set_file(file_)
        document.file_added_at = datetime.now()
        document.filename = self.filename.format(
            doc=document, template=self, data=data,
            date=document.file_added_at)
        document.contenttype = 'plain/text'
        document.filesize = len(file_)
        hash = hashlib.sha256()
        hash.update(file_)
        document.hash = hash.digest()

    def create_file_for(self, document):
        """Create a file and add it in the attachment document

        :param document: attachment document instance
        """
        Parser = self.get_parser()
        data = Parser.serialize(self.model, document.data)
        file_ = self.render(data)
        self.update_document(document, file_, data)

    def check_if_file_must_be_generated(self, document):
        """Return True if the file must generate

        :param document: attachment document instance
        :rtype: bool
        """
        if document.type == 'history':
            return False

        if document.template is not self:
            return False

        if not document.has_file():
            return True

        try:
            if document.file_added_at < self.updated_at:
                return True
        except TypeError:
            return True

        parser = self.get_parser()(self.model)
        return parser.check_if_file_must_be_generated(self, document)

    def check_flush_validity(self):
        if not self.get_template():
            raise TemplateException("No configured template for %r", self)

        if not self.get_parser():
            raise TemplateException("No configured parser for %r", self)

    @classmethod
    def after_update_orm_event(cls, mapper, connection, target):
        target.check_flush_validity()

    @classmethod
    def after_insert_orm_event(cls, mapper, connection, target):
        target.check_flush_validity()
