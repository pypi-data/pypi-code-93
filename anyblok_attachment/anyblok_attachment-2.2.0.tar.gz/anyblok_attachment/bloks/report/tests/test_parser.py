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
class TestParser:

    @pytest.fixture(autouse=True, scope='function')
    def define_registry(self, rollback_registry):
        self.registry = rollback_registry

    def test_serialize(self):
        Parser = self.registry.Attachment.Parser
        model = 'Model.registry.Attachment.Parser'
        data = {'a': 'Data'}
        assert Parser.serialize(model, data) == data

    def test_check_if_file_must_be_generated(self):
        Parser = self.registry.Attachment.Parser
        template = self.registry.Attachment.Template.insert(
            name="test",
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        document = self.registry.Attachment.Document.insert(
            template=template)
        assert not Parser.check_if_file_must_be_generated(template, document)
