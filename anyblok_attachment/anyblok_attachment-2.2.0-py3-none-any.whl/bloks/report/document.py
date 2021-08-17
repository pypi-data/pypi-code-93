# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.relationship import Many2One
Attachment = Declarations.Model.Attachment


@Declarations.register(Attachment)
class Document:

    template = Many2One(model=Attachment.Template)


@Declarations.register(Attachment.Document)
class Latest:

    def get_file(self):
        if self.template:
            if self.template.check_if_file_must_be_generated(self):
                self.template.create_file_for(self)

        return super(Latest, self).get_file()
