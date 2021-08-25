# -*- coding: utf-8 -*-

from collective.behavior.sdg import _
from collective.behavior.sdg.widgets.linked_checkbox import linked_checkbox_field_widget
from plone import schema
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.CMFPlone.utils import safe_hasattr
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import provider


class ISustainableDevelopmentGoalsMarker(Interface):
    pass


@provider(IFormFieldProvider)
class ISustainableDevelopmentGoals(model.Schema):
    """
    """

    sdgs = schema.List(
        title=_(u"SDG"),
        value_type=schema.Choice(
            vocabulary=u"collective.behavior.sdg.SDGsVocabulary",
            required=True,
        ),
        required=False,
    )

    form.widget('sdgs', linked_checkbox_field_widget, links_record='collective.behavior.sdg.sdgs')


@implementer(ISustainableDevelopmentGoals)
@adapter(ISustainableDevelopmentGoalsMarker)
class SustainableDevelopmentGoals(object):
    def __init__(self, context):
        self.context = context

    @property
    def sdgs(self):
        if safe_hasattr(self.context, 'sdgs'):
            return self.context.sdgs
        return None

    @sdgs.setter
    def sdgs(self, value):
        self.context.sdgs = value
