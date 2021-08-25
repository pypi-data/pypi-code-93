# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.behavior.sdg.testing import COLLECTIVE_BEHAVIOR_SDG_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that collective.behavior.sdg is properly installed."""

    layer = COLLECTIVE_BEHAVIOR_SDG_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.behavior.sdg is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.behavior.sdg'))

    def test_browserlayer(self):
        """Test that ICollectiveBehaviorSdgLayer is registered."""
        from collective.behavior.sdg.interfaces import (
            ICollectiveBehaviorSdgLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectiveBehaviorSdgLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_BEHAVIOR_SDG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['collective.behavior.sdg'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.behavior.sdg is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.behavior.sdg'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveBehaviorSdgLayer is removed."""
        from collective.behavior.sdg.interfaces import \
            ICollectiveBehaviorSdgLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            ICollectiveBehaviorSdgLayer,
            utils.registered_layers())
