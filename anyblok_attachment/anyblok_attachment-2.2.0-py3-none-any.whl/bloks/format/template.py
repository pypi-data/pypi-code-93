# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import UUID, String

register = Declarations.register
Attachment = Declarations.Model.Attachment
TYPE = 'format'


@Declarations.register(Attachment)
class Template:

    @classmethod
    def get_template_type(cls):
        res = super(Template, cls).get_template_type()
        res.update({TYPE: 'Simple python format templating'})
        return res


@Declarations.register(Attachment.Template)
class Format(Attachment.Template):
    """Simple python format templating"""
    TYPE = TYPE

    uuid = UUID(
        primary_key=True, nullable=False, binary=False,
        foreign_key=Attachment.Template.use('uuid').options(ondelete='cascade'))
    contenttype = String(nullable=False)

    def render(self, data):
        template = self.get_template()
        return bytes(template.format(**data), encoding='utf-8')

    def update_document(self, document, file_, data):
        super(Format, self).update_document(document, file_, data)
        document.contenttype = self.contenttype
