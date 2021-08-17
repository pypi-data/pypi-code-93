# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.relationship import Many2One


@Declarations.register(Declarations.Mixin)
class WkHtml2Pdf:

    wkhtml2pdf_configuration = Many2One(
        model=Declarations.Model.Attachment.WkHtml2Pdf,
        nullable=False)

    def check_if_file_must_be_generated(self, document):
        """Overwrite to check also if the configuration have changed"""
        conf = self.wkhtml2pdf_configuration
        res = super(WkHtml2Pdf, self).check_if_file_must_be_generated(document)
        if res:
            return True

        if document.file_added_at < conf.updated_at:
            return True

        if document.file_added_at < conf.page.updated_at:
            return True

        return False

    def wkhtml2pdf(self, html_content):
        prefix = '%s-%s' % (str(self.uuid), self.updated_at.isoformat())
        return self.wkhtml2pdf_configuration.cast_html2pdf(
            prefix, html_content)
