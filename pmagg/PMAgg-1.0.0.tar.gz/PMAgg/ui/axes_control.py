# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'axes_control.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide2 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(450, 365)
        Form.setMinimumSize(QtCore.QSize(450, 365))
        Form.setMaximumSize(QtCore.QSize(450, 365))
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(200, 330, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(280, 330, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setGeometry(QtCore.QRect(360, 330, 75, 23))
        self.pushButton_3.setObjectName("pushButton_3")
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 441, 321))
        self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.formLayoutWidget_2 = QtWidgets.QWidget(self.tab_2)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 271, 161))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayout_5 = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.formLayout_5.setContentsMargins(0, 0, 0, 0)
        self.formLayout_5.setObjectName("formLayout_5")
        self.label_19 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_19.setObjectName("label_19")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_19)
        self.comboBox_4 = QtWidgets.QComboBox(self.formLayoutWidget_2)
        self.comboBox_4.setObjectName("comboBox_4")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox_4)
        self.label_21 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_21.setObjectName("label_21")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_21)
        self.comboBox_5 = QtWidgets.QComboBox(self.formLayoutWidget_2)
        self.comboBox_5.setObjectName("comboBox_5")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBox_5)
        self.label_22 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_22.setObjectName("label_22")
        self.formLayout_5.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_22)
        self.comboBox_6 = QtWidgets.QComboBox(self.formLayoutWidget_2)
        self.comboBox_6.setObjectName("comboBox_6")
        self.formLayout_5.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboBox_6)
        self.label_23 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_23.setObjectName("label_23")
        self.formLayout_5.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_23)
        self.comboBox_7 = QtWidgets.QComboBox(self.formLayoutWidget_2)
        self.comboBox_7.setObjectName("comboBox_7")
        self.formLayout_5.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.comboBox_7)
        self.label_24 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_24.setObjectName("label_24")
        self.formLayout_5.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_24)
        self.lineEdit_15 = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_15.setObjectName("lineEdit_15")
        self.formLayout_5.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.lineEdit_15)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.formLayoutWidget = QtWidgets.QWidget(self.tab_3)
        self.formLayoutWidget.setGeometry(QtCore.QRect(0, 10, 341, 131))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout_4 = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout_4.setContentsMargins(0, 0, 0, 0)
        self.formLayout_4.setObjectName("formLayout_4")
        self.label_16 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_16.setObjectName("label_16")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_16)
        self.comboBox = QtWidgets.QComboBox(self.formLayoutWidget)
        self.comboBox.setObjectName("comboBox")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox)
        self.label_17 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_17.setObjectName("label_17")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_17)
        self.comboBox_2 = QtWidgets.QComboBox(self.formLayoutWidget)
        self.comboBox_2.setObjectName("comboBox_2")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBox_2)
        self.label_18 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_18.setObjectName("label_18")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_18)
        self.comboBox_3 = QtWidgets.QComboBox(self.formLayoutWidget)
        self.comboBox_3.setObjectName("comboBox_3")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboBox_3)
        self.label_20 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_20.setObjectName("label_20")
        self.formLayout_4.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_20)
        self.pushButton_4 = QtWidgets.QPushButton(self.formLayoutWidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.formLayout_4.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.pushButton_4)
        self.label = QtWidgets.QLabel(self.tab_3)
        self.label.setGeometry(QtCore.QRect(0, 150, 341, 16))
        self.label.setText("")
        self.label.setObjectName("label")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.formLayoutWidget_3 = QtWidgets.QWidget(self.tab_4)
        self.formLayoutWidget_3.setGeometry(QtCore.QRect(0, 0, 211, 272))
        self.formLayoutWidget_3.setObjectName("formLayoutWidget_3")
        self.formLayout_6 = QtWidgets.QFormLayout(self.formLayoutWidget_3)
        self.formLayout_6.setContentsMargins(0, 0, 0, 0)
        self.formLayout_6.setObjectName("formLayout_6")
        self.label_25 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_25.setObjectName("label_25")
        self.formLayout_6.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_25)
        self.lineEdit_16 = QtWidgets.QLineEdit(self.formLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        self.lineEdit_16.setFont(font)
        self.lineEdit_16.setObjectName("lineEdit_16")
        self.formLayout_6.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_16)
        self.label_27 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_27.setObjectName("label_27")
        self.formLayout_6.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_27)
        self.comboBox_8 = QtWidgets.QComboBox(self.formLayoutWidget_3)
        self.comboBox_8.setObjectName("comboBox_8")
        self.formLayout_6.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBox_8)
        self.label_29 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_29.setObjectName("label_29")
        self.formLayout_6.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_29)
        self.comboBox_12 = QtWidgets.QComboBox(self.formLayoutWidget_3)
        self.comboBox_12.setObjectName("comboBox_12")
        self.formLayout_6.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboBox_12)
        self.label_28 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_28.setObjectName("label_28")
        self.formLayout_6.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_28)
        self.lineEdit_17 = QtWidgets.QLineEdit(self.formLayoutWidget_3)
        self.lineEdit_17.setObjectName("lineEdit_17")
        self.formLayout_6.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lineEdit_17)
        self.label_30 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_30.setObjectName("label_30")
        self.formLayout_6.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_30)
        self.lineEdit_19 = QtWidgets.QLineEdit(self.formLayoutWidget_3)
        self.lineEdit_19.setObjectName("lineEdit_19")
        self.formLayout_6.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.lineEdit_19)
        self.label_31 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_31.setObjectName("label_31")
        self.formLayout_6.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_31)
        self.lineEdit_20 = QtWidgets.QLineEdit(self.formLayoutWidget_3)
        self.lineEdit_20.setObjectName("lineEdit_20")
        self.formLayout_6.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.lineEdit_20)
        self.label_32 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_32.setObjectName("label_32")
        self.formLayout_6.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_32)
        self.comboBox_9 = QtWidgets.QComboBox(self.formLayoutWidget_3)
        self.comboBox_9.setObjectName("comboBox_9")
        self.formLayout_6.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.comboBox_9)
        self.label_33 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_33.setObjectName("label_33")
        self.formLayout_6.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_33)
        self.comboBox_10 = QtWidgets.QComboBox(self.formLayoutWidget_3)
        self.comboBox_10.setObjectName("comboBox_10")
        self.formLayout_6.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.comboBox_10)
        self.formLayoutWidget_4 = QtWidgets.QWidget(self.tab_4)
        self.formLayoutWidget_4.setGeometry(QtCore.QRect(220, 0, 211, 231))
        self.formLayoutWidget_4.setObjectName("formLayoutWidget_4")
        self.formLayout_7 = QtWidgets.QFormLayout(self.formLayoutWidget_4)
        self.formLayout_7.setContentsMargins(0, 0, 0, 0)
        self.formLayout_7.setObjectName("formLayout_7")
        self.label_34 = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.label_34.setObjectName("label_34")
        self.formLayout_7.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_34)
        self.checkBox_2 = QtWidgets.QCheckBox(self.formLayoutWidget_4)
        self.checkBox_2.setText("")
        self.checkBox_2.setObjectName("checkBox_2")
        self.formLayout_7.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.checkBox_2)
        self.label_36 = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.label_36.setObjectName("label_36")
        self.formLayout_7.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_36)
        self.lineEdit_21 = QtWidgets.QLineEdit(self.formLayoutWidget_4)
        self.lineEdit_21.setObjectName("lineEdit_21")
        self.formLayout_7.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_21)
        self.label_37 = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.label_37.setObjectName("label_37")
        self.formLayout_7.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_37)
        self.comboBox_11 = QtWidgets.QComboBox(self.formLayoutWidget_4)
        self.comboBox_11.setObjectName("comboBox_11")
        self.formLayout_7.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboBox_11)
        self.label_38 = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.label_38.setObjectName("label_38")
        self.formLayout_7.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_38)
        self.checkBox_4 = QtWidgets.QCheckBox(self.formLayoutWidget_4)
        self.checkBox_4.setText("")
        self.checkBox_4.setObjectName("checkBox_4")
        self.formLayout_7.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.checkBox_4)
        self.label_39 = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.label_39.setObjectName("label_39")
        self.formLayout_7.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_39)
        self.checkBox_5 = QtWidgets.QCheckBox(self.formLayoutWidget_4)
        self.checkBox_5.setText("")
        self.checkBox_5.setObjectName("checkBox_5")
        self.formLayout_7.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.checkBox_5)
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.gridLayoutWidget = QtWidgets.QWidget(self.tab_5)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 10, 255, 126))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_42 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_42.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_42.setObjectName("label_42")
        self.gridLayout.addWidget(self.label_42, 2, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_40 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_40.setObjectName("label_40")
        self.horizontalLayout_2.addWidget(self.label_40)
        self.lineEdit_18 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_18.setObjectName("lineEdit_18")
        self.horizontalLayout_2.addWidget(self.lineEdit_18)
        self.label_41 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_41.setObjectName("label_41")
        self.horizontalLayout_2.addWidget(self.label_41)
        self.lineEdit_22 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_22.setObjectName("lineEdit_22")
        self.horizontalLayout_2.addWidget(self.lineEdit_22)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)
        self.comboBox_13 = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.comboBox_13.setObjectName("comboBox_13")
        self.gridLayout.addWidget(self.comboBox_13, 0, 1, 1, 1)
        self.lineEdit_23 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_23.setObjectName("lineEdit_23")
        self.gridLayout.addWidget(self.lineEdit_23, 2, 1, 1, 1)
        self.label_35 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_35.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_35.setObjectName("label_35")
        self.gridLayout.addWidget(self.label_35, 1, 0, 1, 1)
        self.label_26 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_26.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_26.setObjectName("label_26")
        self.gridLayout.addWidget(self.label_26, 0, 0, 1, 1)
        self.label_44 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_44.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_44.setObjectName("label_44")
        self.gridLayout.addWidget(self.label_44, 3, 0, 1, 1)
        self.comboBox_14 = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.comboBox_14.setObjectName("comboBox_14")
        self.gridLayout.addWidget(self.comboBox_14, 3, 1, 1, 1)
        self.label_43 = QtWidgets.QLabel(self.tab_5)
        self.label_43.setGeometry(QtCore.QRect(0, 200, 431, 71))
        self.label_43.setStyleSheet("")
        self.label_43.setLineWidth(3)
        self.label_43.setTextFormat(QtCore.Qt.PlainText)
        self.label_43.setObjectName("label_43")
        self.tabWidget.addTab(self.tab_5, "")

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "确定"))
        self.pushButton_2.setText(_translate("Form", "取消"))
        self.pushButton_3.setText(_translate("Form", "应用"))
        self.label_19.setText(_translate("Form", "显示轴："))
        self.label_21.setText(_translate("Form", "网格颜色："))
        self.label_22.setText(_translate("Form", "刻度："))
        self.label_23.setText(_translate("Form", "网格样式："))
        self.label_24.setText(_translate("Form", "网格宽度："))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "网格"))
        self.label_16.setText(_translate("Form", "中文字体："))
        self.label_17.setText(_translate("Form", "英文字体："))
        self.label_18.setText(_translate("Form", "中英文混合字体："))
        self.label_20.setText(_translate("Form", "重新检索字体库："))
        self.pushButton_4.setText(_translate("Form", "start"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Form", "字体"))
        self.label_25.setText(_translate("Form", "坐标样式："))
        self.lineEdit_16.setText(_translate("Form", "(%.2f,%.2f)"))
        self.label_27.setText(_translate("Form", "背景颜色："))
        self.label_29.setText(_translate("Form", "边框颜色："))
        self.label_28.setText(_translate("Form", "边框粗细："))
        self.label_30.setText(_translate("Form", "文字偏移量："))
        self.lineEdit_19.setText(_translate("Form", "(0,0)"))
        self.label_31.setText(_translate("Form", "箭头粗细："))
        self.label_32.setText(_translate("Form", "箭头颜色："))
        self.label_33.setText(_translate("Form", "箭头形状："))
        self.label_34.setText(_translate("Form", "是否显示点："))
        self.label_36.setText(_translate("Form", "文字大小："))
        self.label_37.setText(_translate("Form", "文字颜色："))
        self.label_38.setText(_translate("Form", "是否显示文字："))
        self.label_39.setText(_translate("Form", "是否显示箭头："))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("Form", "注释"))
        self.label_42.setText(_translate("Form", "输出图像分辨率/dpi："))
        self.label_40.setText(_translate("Form", "宽"))
        self.label_41.setText(_translate("Form", "高"))
        self.label_35.setText(_translate("Form", "输出图像尺寸/英寸："))
        self.label_26.setText(_translate("Form", "切换Tab页绘图方式："))
        self.label_44.setText(_translate("Form", "选择默认绘图风格："))
        self.label_43.setText(_translate("Form", "1. 图像的大小和分辨率只有在保存时生效\n"
"2. 图像像素数=图片尺寸/inch×分辨率/dpi\n"
"3. 绘图风格采用SciencePlots包，只会在重新plt.show()后才会生效，文字中含有\n"
"中文可能会报错，默认字体的设置将会无效"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("Form", "绘图"))
