from typing import Generator, List, Sequence

from PyQt5 import QtCore, QtWidgets

from xappt_qt.gui.delegates import SimpleItemDelegate


class CheckList(QtWidgets.QWidget):
    item_changed = QtCore.pyqtSignal(QtWidgets.QListWidgetItem)

    def __init__(self, searchable: bool = False):
        super().__init__()

        self.list = QtWidgets.QListWidget()
        self.setup_ui(searchable)

        self._init_context_menu()

    def setup_ui(self, searchable: bool):
        grid = QtWidgets.QGridLayout()
        self.setLayout(grid)

        list_row = 0
        if searchable:
            edit = QtWidgets.QLineEdit()
            edit.setPlaceholderText("Search")
            edit.setClearButtonEnabled(True)
            edit.textChanged.connect(self._on_filter_changed)
            grid.addWidget(edit, 0, 0)
            list_row = 1

        grid.addWidget(self.list, list_row, 0)

        self.list.setItemDelegate(SimpleItemDelegate())
        # noinspection PyUnresolvedReferences
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list.setAlternatingRowColors(True)
        self.list.setSpacing(2)
        self.list.itemChanged.connect(self._on_item_changed)

    def _init_context_menu(self):
        self.list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.context_menu = QtWidgets.QMenu()

        action_check = QtWidgets.QAction("Check All", self)
        action_check.setData(self.check_all)
        self.context_menu.addAction(action_check)

        action_uncheck = QtWidgets.QAction("Check None", self)
        action_uncheck.setData(self.uncheck_all)
        self.context_menu.addAction(action_uncheck)

        action_selected = QtWidgets.QAction("Check Selected", self)
        action_selected.setData(self.check_selected)
        self.context_menu.addAction(action_selected)

        action_invert = QtWidgets.QAction("Invert Checked", self)
        action_invert.setData(self.invert_checked)
        self.context_menu.addAction(action_invert)

        self.list.customContextMenuRequested.connect(self._on_context_menu)

    def add_item(self, text: str, state: QtCore.Qt.CheckState = QtCore.Qt.Unchecked):
        item = QtWidgets.QListWidgetItem(text)
        # noinspection PyTypeChecker
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(state)
        self.list.addItem(item)

    def add_items(self, items: Sequence[str], state: QtCore.Qt.CheckState = QtCore.Qt.Unchecked):
        for item in items:
            self.add_item(item, state)

    def checked_items(self) -> Generator[str, None, None]:
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                yield item.text()

    def check_all(self):
        self._set_check_state(QtCore.Qt.Checked)

    def uncheck_all(self):
        self._set_check_state(QtCore.Qt.Unchecked)

    def invert_checked(self):
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Checked)

    def check_selected(self):
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.isSelected():
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

    def check_items(self, items: Sequence[str]):
        for item in items:
            for match in self.list.findItems(item, QtCore.Qt.MatchExactly):
                match.setCheckState(QtCore.Qt.Checked)

    def _set_check_state(self, state: QtCore.Qt.CheckState):
        for i in range(self.list.count()):
            self.list.item(i).setCheckState(state)

    def _on_item_changed(self, item: QtWidgets.QListWidgetItem):
        self.item_changed.emit(item)

    def _on_context_menu(self, pos: QtCore.QPoint):
        if len(self.context_menu.actions()) == 0:
            return
        action = self.context_menu.exec_(self.list.mapToGlobal(pos))
        if action is None:
            return
        action_fn = action.data()
        action_fn()

    def _on_filter_changed(self, text: str):
        search_text = text.strip().lower()
        while search_text.count("  "):
            search_text = search_text.replace("  ", " ")
        search_terms = search_text.split()
        for i in range(self.list.count()):
            item = self.list.item(i)
            item_text = item.text().lower()
            matched_terms = True
            for term in search_terms:
                if term not in item_text:
                    matched_terms = False
                    break
            item.setHidden(not matched_terms)
