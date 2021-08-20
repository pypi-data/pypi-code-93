# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from plonetheme_withbarceloneta.dsgov.testing import PLONETHEME_DSGOV_INTEGRATION_TESTING  # noqa: E501

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that plonetheme_withbarceloneta.dsgov is properly installed."""

    layer = PLONETHEME_DSGOV_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if plonetheme_withbarceloneta.dsgov is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'plonetheme_withbarceloneta.dsgov'))

    def test_browserlayer(self):
        """Test that IPlonethemeDsgovLayer is registered."""
        from plonetheme_withbarceloneta.dsgov.interfaces import (
            IPlonethemeDsgovLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IPlonethemeDsgovLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = PLONETHEME_DSGOV_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['plonetheme_withbarceloneta.dsgov'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if plonetheme_withbarceloneta.dsgov is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'plonetheme_withbarceloneta.dsgov'))

    def test_browserlayer_removed(self):
        """Test that IPlonethemeDsgovLayer is removed."""
        from plonetheme_withbarceloneta.dsgov.interfaces import \
            IPlonethemeDsgovLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IPlonethemeDsgovLayer,
            utils.registered_layers())
