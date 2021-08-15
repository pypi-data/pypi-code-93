# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'find_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FindDialog(object):
    def setupUi(self, FindDialog):
        FindDialog.setObjectName("FindDialog")
        FindDialog.resize(320, 376)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FindDialog.sizePolicy().hasHeightForWidth())
        FindDialog.setSizePolicy(sizePolicy)
        FindDialog.setMinimumSize(QtCore.QSize(320, 376))
        FindDialog.setMaximumSize(QtCore.QSize(320, 376))
        FindDialog.setBaseSize(QtCore.QSize(320, 376))
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(FindDialog)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(FindDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.find_text_edit = QtWidgets.QLineEdit(FindDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.find_text_edit.sizePolicy().hasHeightForWidth())
        self.find_text_edit.setSizePolicy(sizePolicy)
        self.find_text_edit.setMinimumSize(QtCore.QSize(0, 24))
        self.find_text_edit.setMaximumSize(QtCore.QSize(16777215, 24))
        self.find_text_edit.setObjectName("find_text_edit")
        self.horizontalLayout.addWidget(self.find_text_edit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupBox = QtWidgets.QGroupBox(FindDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.whole_words_check_box = QtWidgets.QCheckBox(self.groupBox)
        self.whole_words_check_box.setObjectName("whole_words_check_box")
        self.verticalLayout_3.addWidget(self.whole_words_check_box)
        self.match_case_check_box = QtWidgets.QCheckBox(self.groupBox)
        self.match_case_check_box.setObjectName("match_case_check_box")
        self.verticalLayout_3.addWidget(self.match_case_check_box)
        self.number_tags_check_box = QtWidgets.QCheckBox(self.groupBox)
        self.number_tags_check_box.setObjectName("number_tags_check_box")
        self.verticalLayout_3.addWidget(self.number_tags_check_box)
        self.verticalLayout.addWidget(self.groupBox, 0, QtCore.Qt.AlignTop)
        self.groupBox_2 = QtWidgets.QGroupBox(FindDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.header_check_box = QtWidgets.QCheckBox(self.groupBox_2)
        self.header_check_box.setChecked(True)
        self.header_check_box.setObjectName("header_check_box")
        self.verticalLayout_4.addWidget(self.header_check_box)
        self.classes_check_box = QtWidgets.QCheckBox(self.groupBox_2)
        self.classes_check_box.setObjectName("classes_check_box")
        self.verticalLayout_4.addWidget(self.classes_check_box)
        self.tables_check_box = QtWidgets.QCheckBox(self.groupBox_2)
        self.tables_check_box.setChecked(True)
        self.tables_check_box.setObjectName("tables_check_box")
        self.verticalLayout_4.addWidget(self.tables_check_box)
        self.blocks_check_box = QtWidgets.QCheckBox(self.groupBox_2)
        self.blocks_check_box.setChecked(True)
        self.blocks_check_box.setObjectName("blocks_check_box")
        self.verticalLayout_4.addWidget(self.blocks_check_box)
        self.entities_check_box = QtWidgets.QCheckBox(self.groupBox_2)
        self.entities_check_box.setChecked(True)
        self.entities_check_box.setObjectName("entities_check_box")
        self.verticalLayout_4.addWidget(self.entities_check_box)
        self.objects_check_box = QtWidgets.QCheckBox(self.groupBox_2)
        self.objects_check_box.setChecked(False)
        self.objects_check_box.setObjectName("objects_check_box")
        self.verticalLayout_4.addWidget(self.objects_check_box)
        self.verticalLayout.addWidget(self.groupBox_2, 0, QtCore.Qt.AlignTop)
        self.verticalLayout_5.addLayout(self.verticalLayout)
        self.message = QtWidgets.QLabel(FindDialog)
        self.message.setObjectName("message")
        self.verticalLayout_5.addWidget(self.message)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.buttons_layout.setObjectName("buttons_layout")
        self.find_forward_button = QtWidgets.QPushButton(FindDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.find_forward_button.sizePolicy().hasHeightForWidth())
        self.find_forward_button.setSizePolicy(sizePolicy)
        self.find_forward_button.setMinimumSize(QtCore.QSize(0, 0))
        self.find_forward_button.setMaximumSize(QtCore.QSize(200, 100))
        self.find_forward_button.setObjectName("find_forward_button")
        self.buttons_layout.addWidget(self.find_forward_button, 0, QtCore.Qt.AlignBottom)
        self.find_backwards_button = QtWidgets.QPushButton(FindDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.find_backwards_button.sizePolicy().hasHeightForWidth())
        self.find_backwards_button.setSizePolicy(sizePolicy)
        self.find_backwards_button.setMinimumSize(QtCore.QSize(0, 0))
        self.find_backwards_button.setMaximumSize(QtCore.QSize(200, 100))
        self.find_backwards_button.setObjectName("find_backwards_button")
        self.buttons_layout.addWidget(self.find_backwards_button, 0, QtCore.Qt.AlignBottom)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttons_layout.addItem(spacerItem)
        self.close_button = QtWidgets.QPushButton(FindDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.close_button.sizePolicy().hasHeightForWidth())
        self.close_button.setSizePolicy(sizePolicy)
        self.close_button.setMinimumSize(QtCore.QSize(0, 0))
        self.close_button.setMaximumSize(QtCore.QSize(200, 100))
        self.close_button.setToolTip("")
        self.close_button.setObjectName("close_button")
        self.buttons_layout.addWidget(self.close_button, 0, QtCore.Qt.AlignRight|QtCore.Qt.AlignBottom)
        self.verticalLayout_5.addLayout(self.buttons_layout)

        self.retranslateUi(FindDialog)
        QtCore.QMetaObject.connectSlotsByName(FindDialog)

    def retranslateUi(self, FindDialog):
        _translate = QtCore.QCoreApplication.translate
        FindDialog.setWindowTitle(_translate("FindDialog", "Find"))
        self.label.setText(_translate("FindDialog", "Find Text:"))
        self.groupBox.setTitle(_translate("FindDialog", "Options"))
        self.whole_words_check_box.setToolTip(_translate("FindDialog", "Search only whole words in normal mode if checked."))
        self.whole_words_check_box.setText(_translate("FindDialog", "Whole Words"))
        self.match_case_check_box.setToolTip(_translate("FindDialog", "Case sensitive search in normal mode if checked."))
        self.match_case_check_box.setText(_translate("FindDialog", "Match Case"))
        self.number_tags_check_box.setToolTip(_translate("FindDialog", "Ignore numeric DXF tags if checked."))
        self.number_tags_check_box.setText(_translate("FindDialog", "Search in Numeric Tags"))
        self.groupBox_2.setToolTip(_translate("FindDialog", "Select sections to search in."))
        self.groupBox_2.setTitle(_translate("FindDialog", "Search in Sections"))
        self.header_check_box.setText(_translate("FindDialog", "HEADER"))
        self.classes_check_box.setText(_translate("FindDialog", "CLASSES"))
        self.tables_check_box.setText(_translate("FindDialog", "TABLES"))
        self.blocks_check_box.setText(_translate("FindDialog", "BLOCKS"))
        self.entities_check_box.setText(_translate("FindDialog", "ENTITIES"))
        self.objects_check_box.setText(_translate("FindDialog", "OBJECTS"))
        self.message.setText(_translate("FindDialog", "TextLabel"))
        self.find_forward_button.setToolTip(_translate("FindDialog", "or press F3"))
        self.find_forward_button.setText(_translate("FindDialog", "Find &Forward"))
        self.find_backwards_button.setToolTip(_translate("FindDialog", "or press F4"))
        self.find_backwards_button.setText(_translate("FindDialog", "Find &Backwards"))
        self.close_button.setText(_translate("FindDialog", "Close"))
