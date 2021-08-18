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


class Ui_Donate(object):
    def setupUi(self, Donate):
        if not Donate.objectName():
            Donate.setObjectName(u"Donate")
        Donate.resize(719, 182)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Donate.sizePolicy().hasHeightForWidth())
        Donate.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(Donate)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_3 = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.label = QLabel(Donate)
        self.label.setObjectName(u"label")
        self.label.setFrameShadow(QFrame.Plain)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.label_2 = QLabel(Donate)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setScaledContents(False)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_2)

        self.verticalSpacer = QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.label_3 = QLabel(Donate)
        self.label_3.setObjectName(u"label_3")
        font = QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_DonateAddress = QLineEdit(Donate)
        self.lineEdit_DonateAddress.setObjectName(u"lineEdit_DonateAddress")
        font1 = QFont()
        font1.setPointSize(11)
        self.lineEdit_DonateAddress.setFont(font1)
        self.lineEdit_DonateAddress.setCursorPosition(0)
        self.lineEdit_DonateAddress.setReadOnly(True)

        self.horizontalLayout.addWidget(self.lineEdit_DonateAddress)

        self.horizontalSpacer = QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_Copy = QPushButton(Donate)
        self.pushButton_Copy.setObjectName(u"pushButton_Copy")

        self.horizontalLayout.addWidget(self.pushButton_Copy)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer_2 = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.retranslateUi(Donate)

        QMetaObject.connectSlotsByName(Donate)
    # setupUi

    def retranslateUi(self, Donate):
        Donate.setWindowTitle(QCoreApplication.translate("Donate", u"Donate!", None))
        self.label.setText(QCoreApplication.translate("Donate", u"Please consider donating ALGO to this project.", None))
        self.label_2.setText(QCoreApplication.translate("Donate", u"Any donation will be used to fund the development and maintenance of Algo Tides.", None))
        self.label_3.setText(QCoreApplication.translate("Donate", u"Algo Tides will always remain a free and open source app. Donations are on a voluntary basis.", None))
        self.lineEdit_DonateAddress.setText(QCoreApplication.translate("Donate", u"TIDESVS3UR7WQTR5J3M5ADEJVOUUS2C2YOEIU4Z6VTPU2EMQME7PSDK76A", None))
        self.pushButton_Copy.setText(QCoreApplication.translate("Donate", u"Copy address", None))
    # retranslateUi

