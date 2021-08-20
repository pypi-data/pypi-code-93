# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface


class IDSGovControlPanel(Interface):

    submitted = schema.TextLine(
        title=u'Orgão que está submetido',
        description=u'Para ser exibido no cabeçalho do Site',
        required=True,
    )


class DSGovControlPanelForm(RegistryEditForm):
    schema = IDSGovControlPanel
    schema_prefix = "dsgov"
    label = u'DSGov Settings'


DSGovControlPanelView = layout.wrap_form(
    DSGovControlPanelForm, ControlPanelFormWrapper)
