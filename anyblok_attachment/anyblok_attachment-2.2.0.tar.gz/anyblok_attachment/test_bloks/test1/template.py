# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations


@Declarations.register(Declarations.Model.Attachment)
class Template:

    @classmethod
    def get_template_type(cls):
        res = super(Template, cls).get_template_type()
        res.update({'MyTemplate': 'My Template'})
        return res


@Declarations.register(Declarations.Model.Attachment.Template,
                       tablename=Declarations.Model.Attachment.Template)
class MyTemplate(Declarations.Model.Attachment.Template):
    TYPE = 'MyTemplate'

    def render(self, data):
        return self.__class__.file_
