"""This module contains the KeyDialog class."""

from LibGladeApplication import LibGladeApplication


class KeyDialog(LibGladeApplication):

    """This is a baseclass for ciphergui's that have key dialogs.

    The subclass should override the resetForm and applySettings methods.

    """

    def __init__(self, gladeFile):
        """Call LibGladeApplication's constructor."""
        LibGladeApplication.__init__(self, gladeFile)

    def showKeyDialog(self):
        """Show the key dialog for this cipher."""
        self.dialog.show()

    def on_dialog_show(self, w):
        """Call self.resetForm()."""
        self.resetForm()

    def on_dialog_delete_event(self, w, e):
        """Hide the dialog and return True."""
        self.dialog.hide()
        return True

    def on_cancelbutton_clicked(self, w):
        """Hide the dialog."""
        self.dialog.hide()

    def on_applybutton_clicked(self, w):
        """Call self.applySettings()."""
        self.applySettings()

    def on_okbutton_clicked(self, w):
        """Call self.applySettings() and hide the dialog."""
        self.applySettings()
        self.dialog.hide()

    def resetForm(self):
        """Copy the model settings to the form settings."""
        pass

    def applySettings(self):
        """Copy the form settings to the model settings."""
        pass
