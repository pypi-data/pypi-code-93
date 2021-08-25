# -*- coding: utf-8 -*-

from collective.symlink.testing import COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING
from plone import api
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent

import unittest


def test_foo():
    return "foo"


def test_bar():
    return "bar"


class TestSymlinkAdaptedContext(unittest.TestCase):
    layer = COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING

    def setUp(self):
        intids = getUtility(IIntIds)
        self.portal = api.portal.get()
        self.base = api.content.create(
            type="Document",
            id="document",
            title="Title",
            description="Description",
            container=self.portal,
            test="test",
            foo="test",
        )
        self.base.test_method = test_foo
        self.folder = api.content.create(
            type="Folder", id="folder", container=self.portal
        )
        self.link = api.content.create(
            type="symlink",
            id="link",
            symbolic_link=RelationValue(intids.getId(self.base)),
            container=self.folder,
            foo="bar",
        )
        self.link.test_method = test_bar

    def tearDown(self):
        for e in ("folder", "document", "link"):
            if e in self.portal:
                api.content.delete(self.portal[e])

    def test_id(self):
        self.assertEqual("link", self.link.id)

    def test_url(self):
        self.assertEqual("/plone/folder/link", "/".join(self.link.getPhysicalPath()))

    def test_title(self):
        self.assertEqual("Title", self.link.Title())

    def test_description(self):
        self.assertEqual("Description", self.link.Description())

    def test_portal_type(self):
        self.assertEqual("symlink", self.link._link_portal_type)
        self.assertEqual("Document", self.link.portal_type)

    def test_allowed_content_types(self):
        self.assertEqual([], self.link.allowedContentTypes())

    def test_parent(self):
        from Acquisition import aq_parent

        self.assertTrue(self.link.__parent__ == self.folder)
        self.assertTrue(aq_parent(self.link) == self.folder)

    def test_attribute_inheritance(self):
        self.assertEqual("bar", self.link.foo)
        self.assertEqual("test", self.link.test)
        self.assertEqual("bar", self.link.test_method())
        self.assertEqual("foo", self.base.test_method())

    def test_indexed_values(self):
        self.assertEqual("Title", self.base.title)
        self.assertEqual("Description", self.base.description)

        brains = api.content.find(context=self.portal, portal_type="Document")
        self.assertEqual(2, len(brains))
        for b in brains:
            self.assertEqual("Title", b.Title)
            self.assertEqual("Description", b.Description)

        self.base.title = "New Title"
        self.base.description = "New Description"
        notify(ObjectModifiedEvent(self.base))
        brains = api.content.find(context=self.portal, portal_type="Document")
        self.assertEqual(2, len(brains))
        for b in brains:
            self.assertEqual("New Title", b.Title)
            self.assertEqual("New Description", b.Description)
