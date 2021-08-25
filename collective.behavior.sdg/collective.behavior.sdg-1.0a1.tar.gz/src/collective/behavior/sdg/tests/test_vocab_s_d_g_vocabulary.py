# -*- coding: utf-8 -*-
from collective.behavior.sdg.testing import COLLECTIVE_BEHAVIOR_SDG_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import IVocabularyTokenized

import unittest


class SDGVocabularyIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_BEHAVIOR_SDG_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_vocab_s_d_g_vocabulary(self):
        vocab_name = 'collective.behavior.sdg.SDGsVocabulary'
        factory = getUtility(IVocabularyFactory, vocab_name)
        self.assertTrue(IVocabularyFactory.providedBy(factory))

        vocabulary = factory(self.portal)
        self.assertTrue(IVocabularyTokenized.providedBy(vocabulary))
        self.assertEqual(vocabulary.getTerm('13').title, u'Climate action')
