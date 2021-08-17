# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_attachment.config import (
    define_attachment_wkhtml2pdf,
)
from anyblok.tests.test_config import MockArgumentParser


class TestArgsParseOption:

    def test_define_attachment_wkhtml2pdf(self):
        parser = MockArgumentParser()
        define_attachment_wkhtml2pdf(parser)
