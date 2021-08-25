# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from collective.behavior.sdg.testing import COLLECTIVE_BEHAVIOR_SDG_FUNCTIONAL_TESTING
from collective.behavior.sdg.testing import COLLECTIVE_BEHAVIOR_SDG_INTEGRATION_TESTING

import unittest


class IndexerIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_BEHAVIOR_SDG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_sdgs_indexer(self):
        pass


class IndexerFunctionalTest(unittest.TestCase):

    layer = COLLECTIVE_BEHAVIOR_SDG_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
