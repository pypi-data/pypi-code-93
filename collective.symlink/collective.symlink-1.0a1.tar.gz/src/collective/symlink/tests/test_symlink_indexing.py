# -*- coding: utf-8 -*-

from collective.symlink.content.symlink import SymlinkSubItem
from collective.symlink.content.symlink import Symlink
from collective.symlink.testing import COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING
from plone import api
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent

import unittest


class TestSymlinkIndexing(unittest.TestCase):
    layer = COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING

    def setUp(self):
        intids = getUtility(IIntIds)
        self.portal = api.portal.get()
        self.folder = api.content.create(
            type="Folder", id="folder", title="Folder", container=self.portal
        )
        self.document_before = api.content.create(
            type="Document",
            id="document-before",
            title="Title",
            description="Description",
            container=self.folder,
        )
        self.link = api.content.create(
            type="symlink",
            id="link",
            symbolic_link=RelationValue(intids.getId(self.folder)),
            container=self.portal,
        )
        self.document_after = api.content.create(
            type="Document",
            id="document-after",
            title="Title",
            description="Description",
            container=self.folder,
        )
        self.subfolder = api.content.create(
            type="Folder",
            id="subfolder",
            title="SubFolder",
            description="Description",
            container=self.folder,
        )
        self.subfolder_item = api.content.create(
            type="Document",
            id="subfolder-document",
            title="Subfolder Item",
            description="Description",
            container=self.subfolder,
        )

    def tearDown(self):
        for e in ("link", "folder"):
            if e in self.portal:
                api.content.delete(self.portal[e])

    def test_indexing_symlink_folder_on_creation(self):
        """ Ensure that symlink folder are correctly indexed """
        brains = api.content.find(context=self.portal, Title="Folder")
        self.assertEqual(2, len(brains))
        self.assertEqual(["Folder", "Folder"], [b.Title for b in brains])
        self.assertItemsEqual(["folder", "link"], [b.id for b in brains])

    def test_indexing_symlink_subitem_on_creation(self):
        """Ensure that elements that children of a symlink by inheritance
        are correctly indexed"""
        brains = api.content.find(context=self.portal, Title="Title")
        self.assertEqual(4, len(brains))
        self.assertEqual(
            ["Title", "Title", "Title", "Title"], [b.Title for b in brains]
        )
        self.assertItemsEqual(
            ["document-before", "document-before", "document-after", "document-after"],
            [b.id for b in brains],
        )

    def test_indexing_symlink_update(self):
        """Ensure that when the original item is updated, the symlink is updated
        as well"""
        self.folder.title = "New Folder"
        notify(ObjectModifiedEvent(self.folder))
        brains = api.content.find(context=self.portal, Title="New Folder")
        self.assertEqual(2, len(brains))
        self.assertEqual(["New Folder", "New Folder"], [b.Title for b in brains])
        self.assertItemsEqual(["folder", "link"], [b.id for b in brains])

    def test_indexing_symlink_subitem_update(self):
        """Ensure that when a children by inheritance of a symlinked item is updated,
        the symlink subitem is updated as well"""
        self.document_before.title = "New Title"
        notify(ObjectModifiedEvent(self.document_before))
        self.document_after.title = "New Title"
        notify(ObjectModifiedEvent(self.document_after))
        brains = api.content.find(context=self.portal, Title="New Title")
        self.assertEqual(
            ["New Title", "New Title", "New Title", "New Title"],
            [b.Title for b in brains],
        )
        self.assertItemsEqual(
            ["document-before", "document-before", "document-after", "document-after"],
            [b.id for b in brains],
        )

    def test_indexing_symlink_item_uid(self):
        """Ensure that the symlink does not have the same UID as the original item"""
        brains = api.content.find(context=self.portal, Title="Folder")
        self.assertEqual(2, len(brains))
        self.assertEqual(2, len(set([b.UID for b in brains])))

    def test_indexing_symlink_subitem_uid(self):
        """Ensure that the symlink subitems does not have the same UID that can lead
        to errors in multiple situations"""
        brains = api.content.find(context=self.portal, Title="Title")
        self.assertEqual(4, len(brains))
        self.assertEqual(4, len(set([b.UID for b in brains])))
        self.assertEqual(4, len(set([b.getObject().UID() for b in brains])))

    def test_indexing_symlink_subsubitem_uid(self):
        brains = api.content.find(context=self.portal, Title="Subfolder Item")
        self.assertEqual(2, len(brains))
        self.assertEqual(2, len(set([b.UID for b in brains])))
        self.assertEqual(2, len(set([b.getObject().UID() for b in brains])))

    def test_indexing_symlink_subitem_path(self):
        brains = api.content.find(context=self.portal, Title="Title")
        self.assertEqual(4, len(brains))
        paths = [
            "/plone/folder/document-after",
            "/plone/folder/document-before",
            "/plone/link/document-after",
            "/plone/link/document-before",
        ]
        self.assertEqual(paths, sorted([b.getPath() for b in brains]))

    def test_indexing_symlink_subsubitem_path(self):
        brains = api.content.find(context=self.portal, Title="Subfolder Item")
        self.assertEqual(2, len(brains))
        paths = [
            "/plone/folder/subfolder/subfolder-document",
            "/plone/link/subfolder/subfolder-document",
        ]
        self.assertEqual(paths, sorted([b.getPath() for b in brains]))

    def test_indexing_symlink_subitem_portal_type(self):
        brains = api.content.find(context=self.portal, Title="Title")
        self.assertEqual(4, len(brains))
        self.assertEqual(
            ["Document"], list(set([b.getObject().portal_type for b in brains]))
        )
        self.assertEqual(["Document"], list(set([b.portal_type for b in brains])))

    def test_indexing_symlink_subsubitem_portal_type(self):
        brains = api.content.find(context=self.portal, Title="Subfolder Item")
        self.assertEqual(2, len(brains))
        self.assertEqual(["Document"], list(set([b.portal_type for b in brains])))

    def test_traversing_subitem_types(self):
        obj = self.folder
        self.assertFalse(isinstance(obj, SymlinkSubItem))
        self.assertFalse(isinstance(obj, Symlink))
        link = obj = self.portal.unrestrictedTraverse("link")
        self.assertFalse(isinstance(obj, SymlinkSubItem))
        self.assertTrue(isinstance(obj, Symlink))
        obj = obj.unrestrictedTraverse("document-after")
        self.assertTrue(isinstance(obj, SymlinkSubItem))
        self.assertFalse(isinstance(obj, Symlink))
        obj = link.unrestrictedTraverse("subfolder")
        self.assertTrue(isinstance(obj, SymlinkSubItem))
        self.assertFalse(isinstance(obj, Symlink))
        obj = obj.unrestrictedTraverse("subfolder-document")
        self.assertTrue(isinstance(obj, SymlinkSubItem))
        self.assertFalse(isinstance(obj, Symlink))

    def test_traversing_link_access(self):
        link = self.portal["link"]
        self.assertTrue("document-after" in link)
        self.assertFalse("foo" in link)

    def test_traversing_subsubitem_access(self):
        subsubitem = self.portal["link"]["subfolder"]
        self.assertTrue("subfolder-document" in subsubitem)
        self.assertFalse("foo" in subsubitem)
