# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.config import Configuration
from anyblok.column import Integer, DateTime, Selection, String, Boolean
from anyblok.relationship import Many2One
from datetime import datetime
from sqlalchemy import CheckConstraint
import tempfile
import os
import subprocess
import shutil
from .exceptions import PageValidityException, WkHtml2PdfException
from logging import getLogger

register = Declarations.register
Attachment = Declarations.Model.Attachment

logger = getLogger(__name__)


@register(Attachment)
class WkHtml2Pdf:

    id = Integer(primary_key=True, nullable=False)
    label = String(nullable=False)
    created_at = DateTime(nullable=False, default=datetime.now)
    updated_at = DateTime(nullable=False, default=datetime.now,
                          auto_update=True)

    copies = Integer(nullable=False, default=1)
    grayscale = Boolean(default=False)
    lowquality = Boolean(default=False)
    dpi = Integer()
    page_offset = Integer(nullable=False, default=0)
    minimum_font_size = Integer()
    margin_bottom = Integer(nullable=False, default=10)
    margin_left = Integer(nullable=False, default=10)
    margin_right = Integer(nullable=False, default=10)
    margin_top = Integer(nullable=False, default=10)
    orientation = Selection(
        selections={'Landscape': 'Landscape', 'Portrait': 'Portrait'},
        nullable=False, default='Portrait')
    page = Many2One(model='Model.Attachment.WkHtml2Pdf.Page',
                    nullable=False)
    background = Boolean(default=True)
    collate = Boolean(default=True)
    encoding = String(default='utf-8', nullable=False)
    images = Boolean(default=True)
    javascript = Boolean(default=True)
    local_file_access = Boolean(default=True)
    javascript_delay = Integer(nullable=False, default=200)
    load_error_handling = Selection(selections='get_error_handling',
                                    default='abort', nullable=False)
    load_media_error_handling = Selection(selections='get_error_handling',
                                          default='abort', nullable=False)

    @classmethod
    def get_error_handling(cls):
        return {x: x.capitalize() for x in ('abort', 'ignore', 'skip')}

    @classmethod
    def define_table_args(cls):
        table_args = super(WkHtml2Pdf, cls).define_table_args()
        return table_args + (
            CheckConstraint('copies > 0',
                            name="copies_upper_than_0"),
            CheckConstraint('page_offset >= 0',
                            name="offset_upper_than_0"),
            CheckConstraint('margin_bottom >= 0',
                            name="marge_bottom_upper_than_0"),
            CheckConstraint('margin_left >= 0',
                            name="marge_left_upper_than_0"),
            CheckConstraint('margin_right >= 0',
                            name="marge_right_upper_than_0"),
            CheckConstraint('margin_top >= 0',
                            name="marge_top_upper_than_0"),
            CheckConstraint('javascript_delay >= 0',
                            name="js_delay_upper_than_0"),
        )

    def options_from_self(self):
        options = []
        for option in ('margin_bottom', 'margin_right', 'margin_left',
                       'margin_top', 'orientation', 'encoding',
                       'javascript_delay', 'load_error_handling',
                       'load_media_error_handling', 'copies', 'dpi',
                       'minimum_font_size'):
            val = getattr(self, option)
            if val is not None:
                options.append('--' + option.replace('_', '-'))
                options.append(str(val))

        for option in ('grayscale', 'lowquality'):
            val = getattr(self, option)
            if val is not None:
                options.append('--' + option.replace('_', '-'))

        options.extend(self.page.get_options())

        for option in ('background', 'images', 'collate'):
            val = getattr(self, option)
            options.append(('--' if val else '--no-') + option)

        for option in ('javascript', 'local_file_access'):
            val = getattr(self, option)
            options.append(
                ('--enable-' if val else '--disable-') + option.replace('_',
                                                                        '-'))

        return options

    def options_from_configuration(self):
        options = []
        if not Configuration.get('wkhtmltopdf_unquiet'):
            options.append('--quiet')
        if Configuration.get('wkhtmltopdf_debug_javascript'):
            options.append('--debug-javascript')
        else:
            options.append('--no-debug-javascript')

        return options

    def cast_html2pdf(self, prefix, html_content):
        """Cast html document to a pdf document

        :param prefix: prefix use for the tempory document
        :param html_content: html file (bytes)
        :rtype: bytes
        :exception: WkHtml2PdfException
        """
        tmp_dir = tempfile.mkdtemp(prefix + '-html2pdf')
        html_path = os.path.join(tmp_dir, 'in.html')
        pdf_path = os.path.join(tmp_dir, 'out.pdf')

        with open(html_path, 'wb') as fd:
            fd.write(html_content)

        cmd = ['wkhtmltopdf']
        cmd.extend(self.options_from_self())
        cmd.extend(self.options_from_configuration())
        cmd.extend([html_path, pdf_path])

        logger.debug('Rendering PDF, cmd=%r', cmd)
        wkhtmltopdf = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = wkhtmltopdf.communicate()

        if wkhtmltopdf.returncode != 0:
            logger.error("wkhtmltopdf failure with stdout=%r, stderr=%r",
                         out, err)
            raise WkHtml2PdfException(
                (
                    "wkhtmltopdf {cmd} in dir {tmp_dir} failed with code "
                    "{code}, check error log for details"
                ).format(
                    cmd=' '.join(cmd),
                    tmp_dir=tmp_dir, code=wkhtmltopdf.returncode
                )
            )

        logger.debug("wkhtmltopdf finished stdout=%r, stderr=%r", out, err)

        with open(pdf_path, 'rb') as fd:
            file_ = fd.read()

        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            logger.warning("Could not clean up temporary directory %r",
                           tmp_dir, exc_info=True)
        return file_


@register(Attachment.WkHtml2Pdf)
class Page:
    """Define the Page size"""

    label = String(primary_key=True, nullable=False)
    created_at = DateTime(nullable=False, default=datetime.now)
    updated_at = DateTime(nullable=False, default=datetime.now,
                          auto_update=True)

    size = String()
    height = Integer()
    width = Integer()

    @classmethod
    def define_table_args(cls):
        table_args = super(Page, cls).define_table_args()
        return table_args + (
            CheckConstraint(
                '(height is null and width is null) or '
                '(height > 0 and width > 0)',
                name="size_upper_than_0"),
        )

    def get_options(self):
        options = []
        for field in ('size', 'width', 'height'):
            val = getattr(self, field)
            if val:
                options.append('--page-' + field)
                options.append(str(val))

        return options

    def check_flush_validity(self):
        if not self.size and not self.height and not self.width:
            raise PageValidityException(
                "You must define a size or a height and width")

        if self.size:
            self.height = None
            self.width = None

    @classmethod
    def after_update_orm_event(cls, mapper, connection, target):
        target.check_flush_validity()

    @classmethod
    def after_insert_orm_event(cls, mapper, connection, target):
        target.check_flush_validity()
