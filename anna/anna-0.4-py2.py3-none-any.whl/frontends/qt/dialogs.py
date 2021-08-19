# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import pyqt45
from .utils import convert_rst_to_html

Widgets = pyqt45.Widgets


class ComponentInfoDialog(Widgets.QDialog):
    def __init__(self, component, parent=None):
        super(ComponentInfoDialog, self).__init__(parent=parent)

        info_text = Widgets.QTextEdit()
        info_text.setText(convert_rst_to_html(component.__doc__ or ''))
        info_text.setReadOnly(True)

        ok_button = Widgets.QPushButton('Ok', clicked=self.accept)

        v_layout = Widgets.QVBoxLayout()
        v_layout.addWidget(info_text)

        h_layout = Widgets.QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(ok_button)
        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)

        self.setWindowTitle(component.__name__)

        if parent is not None:
            self.resize(int(parent.width() * 0.75), int(parent.height() * 0.50))
