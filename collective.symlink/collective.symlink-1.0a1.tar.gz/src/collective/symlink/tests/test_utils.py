# -*- coding: utf-8 -*-

from collective.symlink.testing import COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING
from collective.symlink.utils import is_linked_object
from plone import api
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield import RelationValue

import unittest


class TestUtils(unittest.TestCase):
    layer = COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING
    maxDiff = None

    def tearDown(self):
        portal = api.portal.get()
        for e in ("link", "document"):
            if e in portal:
                api.content.delete(portal[e])

    def test_is_linked_object(self):
        portal = api.portal.get()
        intids = getUtility(IIntIds)
        folder = api.content.create(type="Folder", id="folder", container=portal)
        doc = api.content.create(
            type="Document",
            id="document",
            title="Title",
            description="Description",
            container=folder,
        )
        link = api.content.create(
            type="symlink",
            id="link",
            symbolic_link=RelationValue(intids.getId(folder)),
            container=portal,
        )
        result = []
        result.append(is_linked_object(doc))
        result.append(is_linked_object(folder))
        result.append(is_linked_object(link))
        # This return the document related to the link : /plone/link/document
        result.append(is_linked_object(link.document))
        result.append(is_linked_object(link["document"]))
        result = [
            (l, s and s.UID() or s, o and o.UID() or o, r) for l, s, o, r in result
        ]
        expected_result = [
            ("", None, None, ""),
            ("", None, None, ""),
            ("symlink", link.UID(), folder.UID(), ""),
            ("symlink", link.UID(), folder.UID(), "document"),
            ("symlink", link.UID(), folder.UID(), "document"),
        ]
        self.assertEqual(expected_result, result)
