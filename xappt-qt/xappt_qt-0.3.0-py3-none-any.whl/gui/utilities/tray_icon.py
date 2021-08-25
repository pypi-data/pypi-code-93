from collections import namedtuple
from typing import Any, Callable, Dict, Optional, Union

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QSystemTrayIcon

MenuAction = namedtuple('TrayIconMenuItem', ('on_activate', 'is_visible', 'data', 'group'))


class TrayIcon(QtCore.QObject):
    def __init__(self, widget: QtWidgets.QWidget, icon: QtGui.QIcon, **kwargs):
        super().__init__()
        self.menu_actions: Dict[str, MenuAction] = {}

        self.on_trigger: Optional[Callable] = kwargs.get('on_trigger')
        self.on_double_click: Optional[Callable] = kwargs.get('on_double_click')
        self.on_middle_click: Optional[Callable] = kwargs.get('on_middle_click')
        self.on_message_click: Optional[Callable] = kwargs.get('on_message_click')

        self.context_menu = QtWidgets.QMenu()

        self.tray_available = QSystemTrayIcon.isSystemTrayAvailable()
        self.messages_available = QSystemTrayIcon.supportsMessages()

        self.tray_icon = QSystemTrayIcon(widget)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setContextMenu(self.context_menu)

        self._connect_signals()

    def show(self):
        if not self.tray_available:
            return
        self._build_context_menu()
        self.tray_icon.show()

    def destroy(self):
        if not self.tray_available:
            return
        self.tray_icon.deleteLater()

    def add_menu_item(self, name: Optional[str], **kwargs):
        on_activate: Optional[Callable] = kwargs.get('on_activate')
        is_visible: Optional[Callable] = kwargs.get('is_visible')
        data: Optional[Any] = kwargs.get('data')
        group: Optional[str] = kwargs.get('group')

        if name is None:
            name = f"--{len(self.menu_actions):02d}"

        self.menu_actions[name] = MenuAction(on_activate, is_visible, data, group)

    def _message(self, title: str, message: str,
                 icon: Union[QSystemTrayIcon.MessageIcon, QtGui.QIcon] = QSystemTrayIcon.Information,
                 delay: int = 10000):
        if not self.tray_available:
            return
        if self.messages_available:
            self.tray_icon.showMessage(title, message, icon, delay)
        else:
            print(f"{title}: {message}")

    def info(self, title: str, message: str, delay: int = 10000):
        self._message(title, message, QSystemTrayIcon.Information, delay)

    def warn(self, title: str, message: str, delay: int = 10000):
        self._message(title, message, QSystemTrayIcon.Warning, delay)

    def critical(self, title: str, message: str, delay: int = 10000):
        self._message(title, message, QSystemTrayIcon.Critical, delay)

    # noinspection PyUnresolvedReferences
    def _connect_signals(self):
        if not self.tray_available:
            return
        self.context_menu.aboutToShow.connect(self._build_context_menu)
        self.context_menu.triggered.connect(self._on_context_menu_action)
        self.tray_icon.messageClicked.connect(self._on_message_clicked)
        self.tray_icon.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.on_double_click is not None:
                self.on_double_click()
        elif reason == QSystemTrayIcon.MiddleClick:
            if self.on_middle_click is not None:
                self.on_middle_click()
        elif reason == QSystemTrayIcon.Trigger:
            if self.on_trigger is not None:
                self.on_trigger()

    def _on_message_clicked(self):
        if self.on_message_click is not None:
            self.on_message_click()

    def _build_context_menu(self):
        self.context_menu.clear()
        submenus = {}
        for name, menu_item in self.menu_actions.items():
            if name.startswith("--"):
                self.context_menu.addSeparator()
            else:
                if menu_item.is_visible is None or menu_item.is_visible():
                    group = menu_item.group
                    if group is not None:
                        submenu = submenus.get(group)
                        if submenu is None:
                            submenu = self.context_menu.addMenu(group)
                            submenus[group] = submenu
                        submenu.addAction(name)
                    else:
                        self.context_menu.addAction(name)

    def _on_context_menu_action(self, action: QtWidgets.QAction):
        if action is None:
            return
        selected_command = action.text()
        menu_action = self.menu_actions[selected_command]
        on_activate = menu_action.on_activate
        if on_activate is not None:
            if menu_action.data is not None:
                on_activate(data=menu_action.data)
                return
            on_activate()
