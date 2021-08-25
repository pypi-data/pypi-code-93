# -*- coding: utf-8 -*-
from collective.behavior.sdg.behaviors.sustainable_development_goals import ISustainableDevelopmentGoalsMarker
from collective.behavior.sdg.testing import COLLECTIVE_BEHAVIOR_SDG_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

import unittest


class SustainableDevelopmentGoalsIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_BEHAVIOR_SDG_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_behavior_sustainable_development_goals(self):
        behavior = getUtility(IBehavior, 'collective.behavior.sdg.sustainable_development_goals')
        self.assertEqual(
            behavior.marker,
            ISustainableDevelopmentGoalsMarker,
        )
