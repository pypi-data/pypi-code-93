# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Info(object):
    def setupUi(self, Info):
        if not Info.objectName():
            Info.setObjectName(u"Info")
        Info.resize(304, 242)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Info.sizePolicy().hasHeightForWidth())
        Info.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(Info)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(Info)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.verticalSpacer_3 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.label_5 = QLabel(Info)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_5)

        self.label_6 = QLabel(Info)
        self.label_6.setObjectName(u"label_6")
        font1 = QFont()
        font1.setPointSize(7)
        self.label_6.setFont(font1)
        self.label_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_6)

        self.verticalSpacer = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.label_2 = QLabel(Info)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_2)

        self.verticalSpacer_2 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.label_3 = QLabel(Info)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_3)

        self.label_4 = QLabel(Info)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setTextFormat(Qt.RichText)
        self.label_4.setAlignment(Qt.AlignCenter)
        self.label_4.setOpenExternalLinks(True)

        self.verticalLayout.addWidget(self.label_4)


        self.retranslateUi(Info)

        QMetaObject.connectSlotsByName(Info)
    # setupUi

    def retranslateUi(self, Info):
        Info.setWindowTitle(QCoreApplication.translate("Info", u"Info", None))
        self.label.setText(QCoreApplication.translate("Info", u"Algo Tides", None))
        self.label_5.setText("")
        self.label_6.setText(QCoreApplication.translate("Info", u"Algo Tides logo\n"
"\u00a9 Giorgio Ciotti 2021. All rights reserved.", None))
        self.label_2.setText(QCoreApplication.translate("Info", u"This software is released under MIT licence.", None))
        self.label_3.setText(QCoreApplication.translate("Info", u"Author: Giorgio Ciotti", None))
        self.label_4.setText(QCoreApplication.translate("Info", u"email: <a href=\"mailto:gciotti.dev@gmail.com\">gciotti.dev@gmail.com</a>", None))
    # retranslateUi

