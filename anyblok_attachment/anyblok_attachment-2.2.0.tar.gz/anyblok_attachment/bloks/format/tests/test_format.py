# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest


@pytest.mark.usefixtures('rollback_registry')
class TestFormat:

    @pytest.fixture(autouse=True, scope='function')
    def define_registry(self, rollback_registry):
        self.registry = rollback_registry

    def test_simple_format(self):
        template = self.registry.Attachment.Template.Format.insert(
            name="test",
            template_path='report-format#=#tests/format.tmpl',
            contenttype='text/html',
            model='Model.System.Blok',
            filename='mypage.html')
        document = self.registry.Attachment.Document.insert(
            template=template,
            data={'title': 'My page', 'description': 'Hello world !!'}
        )
        get_file = document.get_file()
        wanted = {
            'contenttype': 'text/html',
            'file': (
                b'<!doctype html>\n<html>\n    <head>\n        <title>My page'
                b'</title>\n    </head>\n    <body>\n        Hello world !!'
                b'\n    </body>\n</html>\n'
            ),
            'file_added_at': get_file['file_added_at'],
            'filename': 'mypage.html',
            'filesize': 131,
            'hash': (
                b'\xf0\xe2?\xebk\xb4\x15\x0f\xb2\x9cT\x08\xee#\x02\xe2\xbe'
                b'\xa16\x8d\xc8\xcda\x91;\xba2\x9c\x9dUF\x10'
            ),
        }
        assert get_file == wanted
