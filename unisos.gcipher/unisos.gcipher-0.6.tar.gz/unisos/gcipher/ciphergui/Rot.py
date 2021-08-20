"""This module contains the Rot class."""

from os.path import join

from .KeyDialog import KeyDialog
import cipher.Rot
import Const


class Rot(KeyDialog, cipher.Rot.Rot):

    """This class permits the user to select a value for key."""

    def __init__(self):
        """Init the GUI and the cipher."""
        KeyDialog.__init__(self, 
            join(Const.GLADEDIR, "ciphergui", "rot.glade"))
        cipher.Rot.Rot.__init__(self)

    def resetForm(self):
        """Copy the model settings to the form settings."""
        self.key_widget.text = str(self.key)

    def applySettings(self):
        """Copy the form settings to the model settings."""
        self.key = int(self.key_widget.text)
