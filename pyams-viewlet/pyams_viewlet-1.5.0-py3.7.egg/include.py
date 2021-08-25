#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_viewlet.include module

This module is used for Pyramid integration
"""

from chameleon import PageTemplateFile

from pyams_viewlet.provider import ProviderExpr


__docformat__ = 'restructuredtext'


def include_package(config):
    """Pyramid package include"""

    # add translations
    config.add_translation_dirs('pyams_viewlet:locales')

    config.scan()

    PageTemplateFile.expression_types['provider'] = ProviderExpr
