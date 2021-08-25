import fnmatch
import os
import re

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

FILTER_EXT_FILTER = re.compile(r"(?:\*?(?P<ext>\.[a-z0-9_.*-]+))")
FILTER_NAME_FILTER = re.compile(r"(?P<label>.*?)(?:\s?\*?(?P<ext>\.\S+))")


# noinspection PyPep8Naming
class FileEdit(QtWidgets.QWidget):
    # noinspection PyUnresolvedReferences
    onSetFile = QtCore.pyqtSignal(str)

    MODE_OPEN_FILE = 0
    MODE_SAVE_FILE = 1
    MODE_CHOOSE_DIR = 2

    def __init__(self, *, parent=None, accept=None, mode=MODE_OPEN_FILE):
        super(FileEdit, self).__init__(parent=parent)

        self._parent = parent
        self._mode = mode
        self._data = None
        self._accept = []
        self._filter = ''
        self._default_path = None

        self._hLayout = QtWidgets.QHBoxLayout()
        self._lineEdit = QtWidgets.QLineEdit()
        self._btnBrowse = QtWidgets.QToolButton()

        self._btnBrowse.setText('...')
        self._btnBrowse.setAcceptDrops(False)

        self._hLayout.setContentsMargins(0, 0, 0, 0)
        self._hLayout.addWidget(self._lineEdit)
        self._hLayout.addWidget(self._btnBrowse)

        self.setLayout(self._hLayout)

        self._lineEdit.setAcceptDrops(False)
        self._lineEdit.returnPressed.connect(self.onReturnPressed)
        self._lineEdit.editingFinished.connect(self.onReturnPressed)
        self._btnBrowse.clicked.connect(self.onBrowseButton)

        self.setAcceptDrops(True)

        self.setAccept(accept)

    def _set_file(self, filename):
        self._lineEdit.setText(filename)
        if os.path.isdir(filename):
            self._default_path = filename
        elif os.path.isfile(filename):
            self._default_path = os.path.dirname(filename)
        # noinspection PyUnresolvedReferences
        self.onSetFile.emit(filename)

    def setPlaceholderText(self, s):
        self._lineEdit.setPlaceholderText(s)

    def accept(self):
        return self._accept

    def browseButton(self):
        return self._btnBrowse.isVisible()

    def button(self):
        return self._btnBrowse

    def data(self):
        return self._data

    def defaultPath(self):
        return self._default_path

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        drag_file = event.mimeData().urls()[0].toLocalFile()

        if self._mode == self.MODE_CHOOSE_DIR:
            if os.path.isdir(drag_file):
                event.accept()
            return

        if not os.path.isfile(drag_file):
            return

        if len(self._accept):
            for ext in self._accept:
                if fnmatch.fnmatch(drag_file, f"*{ext}"):
                    event.accept()
                    return
        else:
            event.accept()

    def dropEvent(self, event: QtGui.QDropEvent):
        drag_file = event.mimeData().urls()[0].toLocalFile()
        self._set_file(drag_file)

    def filter(self):
        return self._filter

    def lineEdit(self):
        return self._lineEdit

    def _browse_file(self, starting_directory):
        if self._mode == self.MODE_OPEN_FILE:
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
                self._parent, 'Select File', starting_directory, self._filter)
        elif self._mode == self.MODE_SAVE_FILE:
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
                self._parent, 'Select File', starting_directory, self._filter,
                options=QtWidgets.QFileDialog.DontConfirmOverwrite)
        else:
            raise NotImplementedError
        if len(file_name) == 0:
            return
        self._set_file(file_name)

    def _browse_dir(self, starting_directory):
        file_name = QtWidgets.QFileDialog.getExistingDirectory(
            self._parent, 'Select Folder', starting_directory,
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
        if file_name is not None and os.path.isdir(file_name):
            self._set_file(file_name)

    def onBrowseButton(self):
        current_path = self._lineEdit.text()
        if os.path.isdir(current_path):
            starting_directory = current_path
        elif os.path.isdir(os.path.dirname(current_path)):
            starting_directory = os.path.dirname(current_path)
        else:
            starting_directory = self._default_path

        if self._mode == self.MODE_CHOOSE_DIR:
            self._browse_dir(starting_directory)
        else:
            self._browse_file(starting_directory)

    def onReturnPressed(self):
        self._set_file(self._lineEdit.text())

    def setAccept(self, accept):
        self._accept = []
        filter_list = []
        for item in accept or []:
            extensions = FILTER_EXT_FILTER.findall(item)
            if len(extensions) == 0:
                continue
            name_match = FILTER_NAME_FILTER.match(item)
            if name_match is None:
                continue
            self._accept += extensions
            label = name_match.group('label')
            ext = name_match.group('ext')  # first extension, if multiple
            if len(label) == 0:
                label = f"{ext[1:].capitalize()} Files"
            extension_string = " ".join([f"*{ext}" for ext in extensions])
            filter_list.append(f"{label} ({extension_string})")
        self._filter = ";;".join(filter_list)

    def setBrowseButton(self, enable):
        self._btnBrowse.setVisible(enable)

    def setData(self, data):
        self._data = data

    def setDefaultPath(self, path):
        self._default_path = path

    def setFilter(self, f):
        self._filter = f

    def setText(self, filename):
        self._lineEdit.setText(filename)

    def text(self):
        return self._lineEdit.text()
