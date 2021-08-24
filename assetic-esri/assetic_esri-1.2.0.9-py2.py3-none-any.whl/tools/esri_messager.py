import arcpy
import six

from assetic.tools.shared import MessagerBase
from ..tools.dummy_process_dialog import DummyProgressDialog

try:
    import pythonaddins
except ModuleNotFoundError:
    # ArcGIS Pro doesn't have this library
    pass


class EsriMessager(MessagerBase):

    def __init__(self):
        super(EsriMessager, self).__init__()

        self._force_use_arcpy_addmessage = False

        # Test if python 3 and therefore ArcGIS Pro
        if six.PY3 is True:
            self.is_desktop = False
        else:
            # Test if running in desktop.  Affects messaging
            self.is_desktop = True

        try:
            chk = pythonaddins.GetSelectedCatalogWindowPath()
        except (RuntimeError, NameError):
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

    def new_message(self, message, typeid=None):
        """
        Create a message dialogue for user if desktop, else print message
        :param message: the message string for the user
        :param typeid: the type of dialog.  Integer.  optional,Default is none
        :returns: The dialog response as a unicode string, or None
        """
        res = None
        if (self.is_desktop is True) and \
                (self._force_use_arcpy_addmessage is False):
            try:
                res = pythonaddins.MessageBox(
                    message, "Assetic Integration", typeid)
            except RuntimeError:
                print("Assetic Integration: {0}".format(message))
            except Exception as ex:
                print("Unhandled Error: {0}. Message:{1}".format(
                    str(ex), message))
        elif self._force_use_arcpy_addmessage is True:
            arcpy.AddMessage(message)
        else:
            if six.PY3 is True:
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

    @staticmethod
    def display_asset_creation_message(force_use_arcpy, dialog,
                                       lyrname, cnt, selcount):
        if force_use_arcpy:
            # Using the progressor
            arcpy.SetProgressorLabel(
                "Creating Assets for layer {0}.\nProcessing "
                "feature {1} of {2}".format(
                    lyrname, int(cnt), selcount))
            arcpy.SetProgressorPosition()
        else:
            dialog.description = \
                "Creating Assets for layer {0}." \
                "\nProcessing feature {1} of {2}".format(
                    lyrname, int(cnt), selcount)
            dialog.progress = cnt / selcount * 100