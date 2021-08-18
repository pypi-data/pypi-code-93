# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'linecombo_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_TransactionLineCombo(object):
    def setupUi(self, TransactionLineCombo):
        if not TransactionLineCombo.objectName():
            TransactionLineCombo.setObjectName(u"TransactionLineCombo")
        TransactionLineCombo.resize(255, 30)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TransactionLineCombo.sizePolicy().hasHeightForWidth())
        TransactionLineCombo.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(TransactionLineCombo)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit = QLineEdit(TransactionLineCombo)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.comboBox = QComboBox(TransactionLineCombo)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout.addWidget(self.comboBox)


        self.retranslateUi(TransactionLineCombo)

        QMetaObject.connectSlotsByName(TransactionLineCombo)
    # setupUi

    def retranslateUi(self, TransactionLineCombo):
        TransactionLineCombo.setWindowTitle(QCoreApplication.translate("TransactionLineCombo", u"Form", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("TransactionLineCombo", u"Algos", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("TransactionLineCombo", u"microAlgos", None))

    # retranslateUi

