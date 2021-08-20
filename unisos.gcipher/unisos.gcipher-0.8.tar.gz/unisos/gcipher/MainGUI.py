"""This file contains the MainGUI class."""

import gtk
import gnome
import gnome.ui
from os.path import join

from . import Const
from .LibGladeApplication import LibGladeApplication
from .GtkAttributesFacade import GtkAttributesFacade 
from .ciphergui.CipherGUIList import cipherGUIList


class MainGUI(LibGladeApplication):

    """This is the main window for the application.
    
    HACK:  To do cut, copy, and paste I'm using the emit method.  I suspect
    that the PyGTK API will eventually update the TextView class to include the
    methods *_clipboard just as the C API does.
    
    The following private variables are used:

    _last_text_view - This is the last TextView that was focused.

    _cipherGUI - This is an instance of a class from the ciphergui package
    associated with the currently selected cipher.

    _cipherGUIInstances - Whenever a new ciphergui instance is created, it is
    cached here so that its key is not lost when the user switches between
    ciphers.

    """

    def __init__(self):
        """Init the GUI."""
        LibGladeApplication.__init__(self, 
            join(Const.GLADEDIR, "gcipher.glade"))
        self._last_text_view = self.decrypted_text_view
        self._cipherGUIInstances = {}
        self._initCipherMenu()

    def _initCipherMenu(self):
        """Initialize the Cipher menu.

        This menu must be dynamic since it must contain the list of ciphers, so
        it can't be created just using Glade.  Place the menu items before the 
        separator and the "Key..." menu item.

        """
        group = None
        l = cipherGUIList[:]
        l.reverse()
        for i in l:
            (className, guiName, labelName, description) = i
            menuItem = gtk.RadioMenuItem(group, labelName)
            if not group:
                group = menuItem
            menuItem.connect_object("activate", self.on_cipher_activate, 
                className)
            menuItem.show()
            self.cipher_menu.prepend(menuItem)
            setattr(self, className, menuItem)
        self.Gie.emit("activate")

    def on_decrypt_activate(self, w):
        """Decrypt encrypted_text_view and update decrypted_text_view."""
        self._transfer(self.encrypted_text_view, self.decrypted_text_view, 
            self._cipherGUI.decrypt)

    def on_encrypt_activate(self, w):
        """Encrypt decrypted_text_view and update encrypted_text_view."""
        self._transfer(self.decrypted_text_view, self.encrypted_text_view, 
            self._cipherGUI.encrypt)

    def on_cut_activate(self, w):
        """Do self._last_text_view.cut_clipboard."""
        self._last_text_view.emit("cut-clipboard")

    def on_copy_activate(self, w):
        """Do self._last_text_view.copy_clipboard."""
        self._last_text_view.emit("copy-clipboard")

    def on_paste_activate(self, w):
        """Do self._last_text_view.paste_clipboard."""
        self._last_text_view.emit("paste-clipboard")

    def on_clear_activate(self, w):
        """Delete the selected text in self._last_text_view, if appropriate."""
        buf = self._last_text_view.buffer
        if len(buf.selection_bounds):
            buf.delete(*buf.selection_bounds)

    def on_copy_up_activate(self, w):
        """Copy the encrypted text to the decrypted text."""
        self._transfer(self.encrypted_text_view, self.decrypted_text_view, 
            lambda s: s)

    def on_copy_down_activate(self, w):
        """Copy the decrypted text to the encrypted text."""
        self._transfer(self.decrypted_text_view, self.encrypted_text_view, 
            lambda s: s)

    def on_cipher_activate(self, cipherGUIClassName):
        """Update the currently selected ciphergui.

        The ciphergui instances are created and cached on an as needed basis.
        Update the key menu item and button so that they are only sensitive if
        the selected ciphergui has a key dialog.
        
        """
        if cipherGUIClassName in self._cipherGUIInstances:
            self._cipherGUI = self._cipherGUIInstances[cipherGUIClassName]
        else:
            CipherGUIModule = __import__("ciphergui." + cipherGUIClassName, 
                globals(), locals(), cipherGUIClassName)
            CipherGUIClass = getattr(CipherGUIModule, cipherGUIClassName)
            self._cipherGUI = self._cipherGUIInstances[cipherGUIClassName] = (
                CipherGUIClass())
        self.key_button.sensitive = self.key.sensitive = (
            hasattr(self._cipherGUI, "showKeyDialog"))

    def on_key_activate(self, w):
        """Show the key dialog for the currently selected cipher."""
        self._cipherGUI.showKeyDialog()

    def on_contents_activate(self, w):
        """Show the man page."""
        gnome.url_show("man:%s.1" % Const.NAME)

    def on_about_activate(self, w):
        """Show the about dialog."""
        gnome.ui.About(Const.NAME, Const.VERSION, Const.COPYRIGHT, Const.INFO, 
            Const.AUTHORS).show()

    def on_text_view_focus(self, text_view, e):
        """Set self._last_text_view."""
        self._last_text_view = GtkAttributesFacade(text_view)

    def _transfer(self, input_text_view, output_text_view, translator):
        """Basically output_text_view = translator(input_text_view)."""
        in_buf = input_text_view.buffer
        output_text_view.buffer.text = translator(
            in_buf.get_text(in_buf.start_iter, in_buf.end_iter, True))
