# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.z3cform.jsonwidget.testing import COLLECTIVE_Z3CFORM_JSONWIDGET_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that collective.z3cform.jsonwidget is properly installed."""

    layer = COLLECTIVE_Z3CFORM_JSONWIDGET_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.z3cform.jsonwidget is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.z3cform.jsonwidget'))

    def test_browserlayer(self):
        """Test that ICollectiveZ3CformJsonwidgetLayer is registered."""
        from collective.z3cform.jsonwidget.interfaces import (
            ICollectiveZ3CformJsonwidgetLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectiveZ3CformJsonwidgetLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_Z3CFORM_JSONWIDGET_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['collective.z3cform.jsonwidget'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.z3cform.jsonwidget is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.z3cform.jsonwidget'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveZ3CformJsonwidgetLayer is removed."""
        from collective.z3cform.jsonwidget.interfaces import \
            ICollectiveZ3CformJsonwidgetLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            ICollectiveZ3CformJsonwidgetLayer,
            utils.registered_layers())
