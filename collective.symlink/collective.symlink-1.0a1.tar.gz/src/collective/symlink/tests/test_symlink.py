# -*- coding: utf-8 -*-

from collective.symlink.testing import COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING
from plone import api
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield import RelationValue

import unittest


class TestSymlink(unittest.TestCase):
    layer = COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING

    def tearDown(self):
        portal = api.portal.get()
        for e in ("link", "document"):
            if e in portal:
                api.content.delete(portal[e])

    def test_symlink_creation(self):
        intids = getUtility(IIntIds)
        base_content = api.content.create(
            type="Document",
            id="document",
            title="Title",
            description="Description",
            container=api.portal.get(),
        )
        link = api.content.create(
            type="symlink",
            id="link",
            symbolic_link=RelationValue(intids.getId(base_content)),
            container=api.portal.get(),
        )
        self.assertTrue(link.symbolic_link.to_object == base_content)
