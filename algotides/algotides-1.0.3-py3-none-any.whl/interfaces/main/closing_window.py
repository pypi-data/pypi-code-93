# PySide2
from PySide2 import QtWidgets, QtCore


# Tides
#   Miscellaneous
from algotides.interfaces.widgets import LoadingWidget


# TODO disconnect all threads from their signals since they could raise an error that we don't care about
#  because the application is about to close.
class ClosingWindow(QtWidgets.QDialog):
    """
    This class is a window that signals to the user that some tasks are still running and
    the application can't be closed right now.
    """
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent, QtCore.Qt.CustomizeWindowHint)

        self.setWindowTitle("Background tasks")
        self.setFixedSize(220, 70)

        main_layout = QtWidgets.QHBoxLayout(self)

        main_layout.addWidget(LoadingWidget(self, "Waiting for all tasks to close..."))

        closing_timer = QtCore.QTimer(self)
        closing_timer.timeout.connect(self.terminate)
        closing_timer.start(500)

    def terminate(self):
        if QtCore.QThreadPool.globalInstance().activeThreadCount() == 0:
            self.close()
