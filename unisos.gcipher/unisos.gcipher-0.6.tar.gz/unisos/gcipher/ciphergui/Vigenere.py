"""This module contains the Vigenere class."""

from os.path import join

from .KeyDialog import KeyDialog
import cipher.Vigenere
from GtkAttributesFacade import GtkAttributesFacade 
import Const


class Vigenere(KeyDialog, cipher.Vigenere.Vigenere):

    """This class permits the user to select a private key."""

    def __init__(self):
        """Init the GUI and the cipher."""
        KeyDialog.__init__(self, 
            join(Const.GLADEDIR, "ciphergui", "vigenere.glade"))
        cipher.Vigenere.Vigenere.__init__(self)

    def resetForm(self):
        """Copy the model settings to the form settings."""
        self.key_widget.text = self.key

    def applySettings(self):
        """Copy the form settings to the model settings.
        
        If the user has left the key in an invalid state (this should only be
        possible if the entry is completely empty), set the key to 
        self.defaultKey.
        
        """
        key = self.key_widget.text
        if not self.isValidKey(key):
            key = self.defaultKey
        self.key = key

    def on_key_widget_changed(self, key_widget):
        """Don't permit the user to type in invalid characters."""
        key_widget = GtkAttributesFacade(key_widget)
        key_widget.text = "".join(
            [i.lower() for i in key_widget.text if i.isalpha()])
