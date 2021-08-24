# coding: utf-8
"""
    assetic.layertools  (layertools.py)
    Tools to assist with using arcgis integration with assetic
"""
from __future__ import absolute_import

from assetic import AsseticSDK
from assetic.tools.shared import XMLConfigReader


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class Config(object):
    """
    Configuration object for ESRI.

    Unable to inherit from ConfigBase in the assetic python-sdk
    as python2 cannot handle a singleton inheriting from an abstract
    class.
    """

    def __init__(self):
        """
        Constructor of the class.
        """
        self._asseticsdk = None
        self._layerconfig = None
        self.loglevel = None
        self.logfile = None

        self._force_use_arcpy_addmessage = False
        # set the logger for this package (to separate from assetic logger)
        # self.logger = logging.getLogger("assetic_esri")

    @property
    def layerconfig(self):
        if self._layerconfig is None:
            self._layerconfig = XMLConfigReader(self.messager, self.xmlconfigfile,
                                           self.asseticsdk)

        return self._layerconfig

    @property
    def asseticsdk(self):
        if self._asseticsdk is None:
            self._asseticsdk = AsseticSDK(self.inifile, self.logfile, self.loglevelname)

        return self._asseticsdk

    @property
    def force_use_arcpy_addmessage(self):
        """
        Return boolean whether to use arcpy.AddMessage for messages
        instead of pythonaddins or other message types
        Useful for scripts run from model builder
        """
        return self._force_use_arcpy_addmessage

    @force_use_arcpy_addmessage.setter
    def force_use_arcpy_addmessage(self, value):
        """
        Return boolean whether to use arcpy.AddMessage for messages
        instead of pythonaddins or other message types
        Useful for scripts run from model builder
        """
        self._force_use_arcpy_addmessage = value
