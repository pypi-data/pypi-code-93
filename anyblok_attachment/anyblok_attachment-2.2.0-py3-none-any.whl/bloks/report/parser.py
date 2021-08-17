# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations


@Declarations.register(Declarations.Model.Attachment)
class Parser:
    """Base parser to serialize the data for templating"""

    def __init__(self, model):
        self.model = model

    @classmethod
    def serialize(cls, model, data):
        """Serialize the data to be understanding by template

        :param model: an anyblok model need to serialize
        :param data: json dict
        :return: json dict
        """
        return data

    @classmethod
    def check_if_file_must_be_generated(cls, template, document):
        """Return a boolean to know if the file must be generate or not

        :param template: template intance
        :param document: latest document instance
        :return: bool
        """
        return False
