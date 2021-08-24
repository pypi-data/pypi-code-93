# coding: utf-8
"""
    assetic_esri.tools.commontools  (commontools.py)
    Tools to assist with using arcgis integration with assetic
"""
from __future__ import absolute_import

import arcpy
import assetic_esri.config

try:
    import pythonaddins
except:
    #ArcGIS Pro doesn't have this library
    pass
import six
import logging

class CommonTools(object):
    """
    Class of tools to support app
    """

    def __init__(self):
        self._force_use_arcpy_addmessage = False

        # Test if python 3 and therefore ArcGIS Pro
        if six.PY3 == True:
            self.logger = logging.getLogger(__name__)
            self.is_desktop = False
            return

        self.logger = logging.getLogger(__name__)
        
        # Test if running in desktop.  Affects messaging
        self.is_desktop = True
        try:
            chk = pythonaddins.GetSelectedCatalogWindowPath()
        except RuntimeError:
            self.is_desktop = False

        
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
        
    def new_message(self,message,typeid = None):
        """
        Create a message dialogue for user if desktop, else print message
        :param message: the message string for the user
        :param typeid: the type of dialog.  Integer.  optional,Default is none
        :returns: The dialog response as a unicode string, or None
        """
        res = None
        if self.is_desktop == True and \
        self._force_use_arcpy_addmessage == False:
            try:
                res = pythonaddins.MessageBox(
                    message,"Assetic Integration",typeid)
            except RuntimeError:
                print("Assetic Integration: {0}".format(message))
            except Exception as ex:
                print("Unhandled Error: {0}. Message:{1}".format(
                    str(ex),message))
        elif self._force_use_arcpy_addmessage == True:
            arcpy.AddMessage(message)
        else:
            if six.PY3 == True:
                arcpy.AddMessage(message)
            else:
                self.logger.info("Assetic Integration: {0}".format(
                    message))
        return res

    def get_progress_dialog(self, force_arcpy_msgs, lyrname, max_range):
        """
        Returns a progress dialog to indicate updating assets using the
        arcpy progress dialog class.
        """
        arcpy_kwargs = {
            "type": "step",
            "message": "Updating assets for layer {0}".format(lyrname),
            "min_range": 0,
            "max_range": max_range,
            "step_value": 1
        }

        if self.is_desktop:
            if force_arcpy_msgs:
                # Set the progressor which provides feedback via the script
                # tool dialogue
                arcpy.SetProgressor(**arcpy_kwargs)
                # need to set a dummy progress tool becuase futher down need
                # to use a with in case using the pythonaddin.ProgressDialogue
                progress_tool = DummyProgressDialog()
            else:
                # desktop via addin, so give user a progress dialog.
                # This progress tool is set with a 'with' further down
                # This dialogue is slow and a little unreliable for large
                # selection sets.
                progress_tool = pythonaddins.ProgressDialog
        else:
            # not desktop so give use dummy progress dialog.
            progress_tool = DummyProgressDialog()

        return progress_tool


class DummyProgressDialog():
    """
    This class is used when not running arcMap in desktop mode since the
    pythonaddins ProgressDialog will have an exception.  It has to be run
    via a with statement, so this class provides an alternate with statement
    """
    def __init__(self):
        pass

    def __enter__(self):
        return True
    
    def __exit__(self,*args):
        return False
