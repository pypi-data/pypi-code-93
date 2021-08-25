# -*- coding: utf-8 -*-
from collective.symlink.content.symlink import ISymlink
from collective.symlink.interfaces import ISymlinkSource
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer


@indexer(IDexterityContent)
def symlink_status_index(obj):
    status = ""
    if ISymlink.providedBy(obj):
        status = "link"
    elif ISymlinkSource.providedBy(obj):
        status = "source"
    else:
        status = "void"
    return status
