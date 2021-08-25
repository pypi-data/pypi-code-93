# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveSymlinkLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ISymlinkSource(Interface):
    """Marker interface that defines symlinks source."""
