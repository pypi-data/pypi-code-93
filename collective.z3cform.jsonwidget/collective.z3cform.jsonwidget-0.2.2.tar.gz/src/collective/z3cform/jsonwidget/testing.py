# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.z3cform.jsonwidget


class CollectiveZ3CformJsonwidgetLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.z3cform.jsonwidget)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.z3cform.jsonwidget:default')


COLLECTIVE_Z3CFORM_JSONWIDGET_FIXTURE = CollectiveZ3CformJsonwidgetLayer()


COLLECTIVE_Z3CFORM_JSONWIDGET_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_Z3CFORM_JSONWIDGET_FIXTURE,),
    name='CollectiveZ3CformJsonwidgetLayer:IntegrationTesting',
)


COLLECTIVE_Z3CFORM_JSONWIDGET_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_Z3CFORM_JSONWIDGET_FIXTURE,),
    name='CollectiveZ3CformJsonwidgetLayer:FunctionalTesting',
)


COLLECTIVE_Z3CFORM_JSONWIDGET_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_Z3CFORM_JSONWIDGET_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveZ3CformJsonwidgetLayer:AcceptanceTesting',
)
