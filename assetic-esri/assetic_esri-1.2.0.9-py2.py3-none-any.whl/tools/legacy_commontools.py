"""
This class is retained so that existing scripts do not fail
The functionality is now predominantly in the common assetic sdk
"""
from assetic_esri import Config
import warnings

class CommonTools(object):
    """
    Class of tools to support app
    """

    def __init__(self):
        self._config = Config()
        self._force_use_arcpy_addmessage = False

    @property
    def force_use_arcpy_addmessage(self):
        """
        Return boolean whether to use arcpy.AddMessage for messages
        instead of pythonaddins or other message types
        Useful for scripts run from model builder
        """
        warnings.warn(
            '"assetic_esri.CommonTools.force_use_arcpy_addmessage" '
            'is deprecated'
            ', "use assetic_esri.config.force_use_arcpy_addmessage" instead',
            stacklevel=2)
        self._force_use_arcpy_addmessage = \
            self._config.force_use_arcpy_addmessage
        return self._force_use_arcpy_addmessage

    @force_use_arcpy_addmessage.setter
    def force_use_arcpy_addmessage(self, value):
        """
        Return boolean whether to use arcpy.AddMessage for messages
        instead of pythonaddins or other message types
        Useful for scripts run from model builder
        """
        warnings.warn(
            '"assetic_esri.CommonTools.force_use_arcpy_addmessage" '
            'is deprecated'
            ', "use assetic_esri.config.force_use_arcpy_addmessage" instead',
            stacklevel=2)
        self._force_use_arcpy_addmessage = value
        self._config.force_use_arcpy_addmessage = value

