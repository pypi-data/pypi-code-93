# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import plonetheme.dsgov


class PlonethemeDsgovLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=plonetheme.dsgov)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plonetheme.dsgov:default')


PLONETHEME_DSGOV_FIXTURE = PlonethemeDsgovLayer()


PLONETHEME_DSGOV_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONETHEME_DSGOV_FIXTURE,),
    name='PlonethemeDsgovLayer:IntegrationTesting',
)


PLONETHEME_DSGOV_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONETHEME_DSGOV_FIXTURE,),
    name='PlonethemeDsgovLayer:FunctionalTesting',
)


PLONETHEME_DSGOV_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PLONETHEME_DSGOV_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='PlonethemeDsgovLayer:AcceptanceTesting',
)
