#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_viewlet.interfaces module

The module defines viewlet and viewlets manager interfaces.
"""

from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Attribute
from zope.interface.common.mapping import IReadMapping
from zope.schema import Bool, List, Object


__docformat__ = 'restructuredtext'


class IViewlet(IContentProvider):
    """A content provider that is managed by another content provider, known
    as viewlet manager.

    Note that you *cannot* call viewlets directly as a provider, i.e. through
    the TALES ``provider`` expression, since it always has to know its manager.
    """

    manager = Attribute("""The Viewlet Manager

                        The viewlet manager for which the viewlet is registered. The viewlet
                        manager will contain any additional data that was provided by the
                        view.
                        """)


class IViewletManager(IContentProvider, IReadMapping):
    """A component that provides access to the content providers.

    The viewlet manager's responsibilities are:

      (1) Aggregation of all viewlets registered for the manager.

      (2) Apply a set of filters to determine the availability of the
          viewlets.

      (3) Sort the viewlets based on some implemented policy.

      (4) Provide an environment in which the viewlets are rendered.

      (5) Render itself by rendering the HTML content of the viewlets.
    """

    manager = Attribute("The ViewletManager to which this manager is attached if also "
                        "defined as a viewlet")

    permission = Attribute("Permission required to display the viewlet manager")

    template = Attribute("Chameleon template used for rendering")

    viewlets = List(title="Viewlets list",
                    value_type=Object(schema=IViewlet))

    render_empty = Bool(title="Render when empty?",
                        default=False)

    def filter(self, viewlets):
        """Filter manager viewlets"""

    def sort(self, viewlets):
        """Sort manager viewlets"""

    def reset(self):
        """Reset manager status; this can be required if the manager between renderings"""
