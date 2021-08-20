from Products.CMFPlone.utils import getFSVersionTuple
from ftw.upgrade import UpgradeStep


class RemoveJsDependencyOnPlone(UpgradeStep):
    """Remove js dependency on plone.
    """

    def __call__(self):
        if getFSVersionTuple() > (5, ):
            self.install_upgrade_profile()
