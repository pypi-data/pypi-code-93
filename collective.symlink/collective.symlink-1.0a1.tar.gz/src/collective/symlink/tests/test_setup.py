# -*- coding: utf-8 -*-
"""Setup tests for this package."""

from collective.symlink.testing import COLLECTIVE_SYMLINK_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

import unittest
import pkg_resources

try:
    pkg_resources.get_distribution("Products.CMFPlone.utils.get_installer")
except pkg_resources.DistributionNotFound:
    HAS_PLONE5 = False
else:
    HAS_PLONE5 = True
    from Products.CMFPlone.utils import get_installer


class TestSetup(unittest.TestCase):
    """Test that collective.symlink is properly installed."""

    layer = COLLECTIVE_SYMLINK_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if HAS_PLONE5:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if collective.symlink is installed."""
        if HAS_PLONE5:
            self.assertTrue(self.installer.is_product_installed("collective.symlink"))
        else:
            self.assertTrue(self.installer.isProductInstalled("collective.symlink"))

    def test_browserlayer(self):
        """Test that ICollectiveSymlinkLayer is registered."""
        from collective.symlink.interfaces import ICollectiveSymlinkLayer
        from plone.browserlayer import utils

        self.assertIn(ICollectiveSymlinkLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_SYMLINK_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if HAS_PLONE5:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        if HAS_PLONE5:
            self.installer.uninstall_product("collective.symlink")
        else:
            self.installer.uninstallProducts(["collective.symlink"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.symlink is cleanly uninstalled."""
        if HAS_PLONE5:
            self.assertFalse(self.installer.is_product_installed("collective.symlink"))
        else:
            self.assertFalse(self.installer.isProductInstalled("collective.symlink"))

    def test_browserlayer_removed(self):
        """Test that ICollectiveSymlinkLayer is removed."""
        from collective.symlink.interfaces import ICollectiveSymlinkLayer
        from plone.browserlayer import utils

        self.assertNotIn(ICollectiveSymlinkLayer, utils.registered_layers())
