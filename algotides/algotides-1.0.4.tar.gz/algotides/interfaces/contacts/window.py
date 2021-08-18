"""
This file describes the contact window, its child widgets and some data structure needed.
"""


# Python
from functools import partial
from sys import stderr


# PySide2
from PySide2 import QtWidgets, QtGui, QtCore


# Tides
#   Miscellaneous
from algotides.structures import ListJsonContacts
import algotides.constants as constants
import algotides.serialization as serialization
from algotides.exceptions import TidesBadEncoding
#   Interfaces
from algotides.interfaces.contacts.ui_window import Ui_ContactsWindow
from algotides.interfaces.contacts.manage.window import ContactManaging
from algotides.interfaces.contacts.widgets import ContactListItem, ContactListWidget


# TODO An empty contact list should still display something (E.g.: Widget "Your contact list is empty")
# TODO Make sure the window is narrower and the address get collapsed like "AAAAAA.....AAAAAA" if the width exceeds
#  the window
class ContactsWindow(QtWidgets.QDialog, Ui_ContactsWindow):
    """
    This class is the contact window.

    This class also manage all information about contacts. It will load at the start of the program all permanent
    information about user contacts so that other classes that need those information will find it here.
    """
    # These icons are static because we want to avoid having to reload them from the disk each time this class is
    #  instantiated.
    icon_search = QtGui.QIcon(":/icons/search.png")
    icon_edit = QtGui.QIcon(":/icons/edit.png")
    icon_delete = QtGui.QIcon(":/icons/delete.png")

    # This list will host the content of the contacts.json file. This is static because other classes might need to
    #  read contacts and create their own widgets.
    #  However this class will be the only one to load it and change it. Other classes shall only read from it.
    # A crucial point is that this list gets loaded with the static method load_contacts_json_file as soon as this
    #  class is done with the definition because other class might need its data even if this class never
    #  gets instantiated.
    jpickled_contacts = None

    # We make a list of ContactListWidget static because each item has a profile pic that could create IO bottleneck
    #  if it has to be loaded each time this class is instantiated.
    # However we create the list of widget for Contacts only the first time that this class is
    #  instantiated because only this class needs its ContactListWidget.
    # This list remains coherent with jpickled_contacts and DOES NOT need to be fully updated as long as
    #  contacts are managed through this class methods.
    contact_widgets = list()

    def __init__(self, parent: QtWidgets.QWidget):
        # This line is necessary because a widget gets it's own window if it doesn't have a parent OR
        #  if it has a parent but has QtCore.Qt.Window flag set.
        super().__init__(parent, QtCore.Qt.WindowCloseButtonHint)

        # Anti memory leak
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setupUi(self)

        self.listWidget.set_item_type(ContactListItem)

        # Setup interface
        #   MenuBar
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBarAction = self.menuBar.addAction("New contact")
        self.verticalLayout.setMenuBar(self.menuBar)
        self.menuBar.setNativeMenuBar(False)

        #   Search bar
        self.lineEdit.addAction(self.icon_search, QtWidgets.QLineEdit.LeadingPosition)
        # End setup

        # Connections
        self.lineEdit.textChanged.connect(self.filter_contacts)
        self.listWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.menuBarAction.triggered.connect(self.new_contact)

        QtCore.QTimer.singleShot(0, self.setup_logic)

    def setup_logic(self):
        # Populate contact_widgets with info from json file.
        if not ContactsWindow.contact_widgets:
            for contact in ContactsWindow.jpickled_contacts:
                ContactsWindow.contact_widgets.append(ContactListWidget(contact))

        # Populate list
        for widget in self.contact_widgets:
            self.listWidget.add_widget(widget)

        # If we enable sorting we get an error when we add an item without widget because list doesn't know
        #  how to compare ContactsListItem without a ContactsListWidget inside.
        #  You can't insert the widget inside the item and then insert item inside the list.
        self.listWidget.sortItems()

    def closeEvent(self, arg__1: QtGui.QCloseEvent):
        # If we don't do this the widgets get deleted from their parent when the window closes.
        #  Typically this would be fine but since we are storing the widgets statically we don't want them deleted.
        for contact in self.contact_widgets:
            contact.setParent(None)

        arg__1.accept()

    @QtCore.Slot(QtCore.QPoint)
    def show_context_menu(self, pos: QtCore.QPoint):
        item = self.listWidget.itemAt(pos)
        if item:
            widget = self.listWidget.itemWidget(item)

            menu = QtWidgets.QMenu(self)
            menu.addAction(self.icon_edit, "Edit", partial(self.edit_contact, item))
            menu.addAction(self.icon_delete, "Delete", partial(self.delete_contact, item))
            menu.addAction("Copy address to clipboard", partial(
                QtGui.QGuiApplication.clipboard().setText, widget.contact.address)
            )

            global_pos = self.listWidget.mapToGlobal(pos)
            menu.exec_(global_pos)

            # This should get rid of the whole object along with the partial.
            menu.deleteLater()

    # This predicate will check if a string "str1" matches against another string "str2" using this logic:
    #   For any substring of str1 separated by space, each substring must be present in str2 taken as is.
    #   For substring of str1 the first match in str2 is searched and removed from both str1 and str2.
    #   If at the end of the procedure str1 is reduced to an empty string then this function returns True,
    #   False otherwise.
    # The logic behind this is that we want to create a 1:1 mapping (bijection) between tokens of str1 and
    #   substrings of str2.
    # This operation is, of course, not commutative. matches("Jo", "Joe") is True, matches("Joe", "Jo") is False.
    @staticmethod
    def is_a_match(str1: str, str2: str) -> bool:
        # I know this for loop should be written as an "all()" but we mutate str2 for every iteration. Maybe in the
        #   future I'll write it in a more functional way.

        # We want to do case-insensitive match.
        str1, str2 = str1.lower(), str2.lower()

        for token in str1.split(" "):
            found = str2.find(token)

            if found != -1:
                # Remove token from str2.
                # We use a generator because if we used string slicing we would have to deal with "out of bound" errors.
                #   Generator might be slower but it's faster to write and more "provably" correct.
                str2 = "".join(str2[i] for i in range(len(str2)) if not (found <= i < found + len(token)))
            else:
                return False

        return True

    @QtCore.Slot(str)
    def filter_contacts(self, new_text: str):
        """
        This method show only those ContactListItems that fit the new search bar content. Hides the rest.
        """
        for i in range(self.listWidget.count()):
            widget = self.listWidget.itemWidget(self.listWidget.item(i))

            # I think this formula reflects quite well the statement:
            #   "Hide this widget only when it doesn't match the name or the address".
            self.listWidget.item(i).setHidden(
                not (
                    ContactsWindow.is_a_match(new_text, widget.contact.name)
                    or
                    widget.contact.address.startswith(new_text)
                )
            )

    @QtCore.Slot()
    def new_contact(self):
        new_contact_window = ContactManaging(self)

        if new_contact_window.exec_() == QtWidgets.QDialog.Accepted:
            new_widget = new_contact_window.return_value

            self.jpickled_contacts.append(new_widget.contact)
            self.contact_widgets.append(new_widget)
            self.listWidget.add_widget(new_widget)

        self.listWidget.sortItems()

    @QtCore.Slot(ContactListItem)
    def edit_contact(self, item: ContactListItem):
        edit_contact_window = ContactManaging(self, self.listWidget.itemWidget(item))

        if edit_contact_window.exec_() == QtWidgets.QDialog.Accepted:
            old_widget, new_widget = self.listWidget.itemWidget(item), edit_contact_window.return_value
            old_contact, new_contact = old_widget.contact, new_widget.contact

            self.remove_item(item)
            self.jpickled_contacts.remove(old_contact)
            if old_contact.pic_name != new_contact.pic_name:
                old_contact.release()
            self.jpickled_contacts.append(new_contact)
            ContactsWindow.contact_widgets.append(new_widget)
            self.listWidget.add_widget(new_widget)

        self.listWidget.sortItems()

    @QtCore.Slot(ContactListItem)
    def delete_contact(self, item: ContactListItem):
        contact = self.listWidget.itemWidget(item).contact

        self.remove_item(item)
        self.jpickled_contacts.remove(contact)
        contact.release()

    # N.B.: The next method that end in "_item" is only "macro" to manage items in the list
    #  to really delete a contact from persistent memory use methods that end in "_contact".
    def remove_item(self, item: ContactListItem):
        widget = self.listWidget.itemWidget(item)

        self.listWidget.takeItem(self.listWidget.row(item))
        ContactsWindow.contact_widgets.remove(widget)

    @staticmethod
    def initialize():
        constants.PATH_THUMBNAILS.mkdir(exist_ok=True)

        if not constants.PATH_CONTACTS_JPICKLE.exists():
            serialization.dump_jpickle(constants.PATH_CONTACTS_JPICKLE, ListJsonContacts())

        ContactsWindow.jpickled_contacts = serialization.load_jpickle(constants.PATH_CONTACTS_JPICKLE)
        if isinstance(ContactsWindow.jpickled_contacts, ListJsonContacts):
            ContactsWindow.jpickled_contacts.save_state()
        else:
            raise TidesBadEncoding(
                constants.PATH_CONTACTS_JPICKLE,
                type(ContactsWindow.jpickled_contacts),
                type(ListJsonContacts())
            )

    @staticmethod
    def shut_down():
        if ContactsWindow.jpickled_contacts.has_changed():
            try:
                serialization.dump_jpickle(
                    constants.PATH_CONTACTS_JPICKLE,
                    ContactsWindow.jpickled_contacts
                )
            except IOError:
                print(f"Could not dump content into {constants.PATH_CONTACTS_JPICKLE}", file=stderr)
