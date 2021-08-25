# -*- coding: utf-8 -*-

from collective.behavior.sdg.behaviors.sustainable_development_goals import ISustainableDevelopmentGoalsMarker
from plone.indexer import indexer
from Products.CMFPlone.utils import base_hasattr
from Products.PluginIndexes.common.UnIndex import _marker as common_marker


@indexer(ISustainableDevelopmentGoalsMarker)
def sdgs(obj):
    """Calculate and return the value for the indexer"""
    if base_hasattr(obj, 'sdgs'):
        return obj.sdgs
    return common_marker
