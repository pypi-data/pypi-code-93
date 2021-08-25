# -*- coding: utf-8 -*-

# from plone import api
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class SDGsVocabulary(object):
    """
        Vocabulary of all sdgs
    """

    def __call__(self, context):
        terms = []
        for nb in range(1, 18):
            key = '{:02d}'.format(nb)
            terms.append(SimpleVocabulary.createTerm(key, key,
                                                     translate('{}_title'.format(key), domain='collective.behavior.sdg',
                                                               context=context.REQUEST)))
        return SimpleVocabulary(terms)


SDGsVocabularyFactory = SDGsVocabulary()
