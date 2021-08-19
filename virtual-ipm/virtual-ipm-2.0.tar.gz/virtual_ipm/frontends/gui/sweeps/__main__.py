import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QCoreApplication, Qt

from .main import SweepWindow


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_X11InitThreads)
    app = QApplication(sys.argv)
    main_window = SweepWindow()
    main_window.show()
    app.exec_()
