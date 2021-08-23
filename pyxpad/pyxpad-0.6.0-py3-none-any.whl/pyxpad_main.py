# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyxpad_main.ui'
#
# Created: Fri Oct  7 15:25:29 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

# Hand-edited to make it work with Qt4 & Qt5
from Qt import QtCore, __qt_version__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

if __qt_version__.split(".")[0] == "5":
    UnicodeUTF8 = 0
else:
    UnicodeUTF8 = QApplication.UnicodeUTF8
# end of hand-edits
from .console_widget import ConsoleWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1069, 762)
        self.actionLoadState = QAction(MainWindow)
        self.actionLoadState.setObjectName(u"actionLoadState")
        self.actionSaveState = QAction(MainWindow)
        self.actionSaveState.setObjectName(u"actionSaveState")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionXPAD_tree = QAction(MainWindow)
        self.actionXPAD_tree.setObjectName(u"actionXPAD_tree")
        self.actionNetCDF_file = QAction(MainWindow)
        self.actionNetCDF_file.setObjectName(u"actionNetCDF_file")
        self.actionPlot = QAction(MainWindow)
        self.actionPlot.setObjectName(u"actionPlot")
        self.actionOPlot = QAction(MainWindow)
        self.actionOPlot.setObjectName(u"actionOPlot")
        self.actionMPlot = QAction(MainWindow)
        self.actionMPlot.setObjectName(u"actionMPlot")
        self.actionXYPlot = QAction(MainWindow)
        self.actionXYPlot.setObjectName(u"actionXYPlot")
        self.actionZPlot = QAction(MainWindow)
        self.actionZPlot.setObjectName(u"actionZPlot")
        self.actionBOUT_data = QAction(MainWindow)
        self.actionBOUT_data.setObjectName(u"actionBOUT_data")
        self.actionContour = QAction(MainWindow)
        self.actionContour.setObjectName(u"actionContour")
        self.actionContour_filled = QAction(MainWindow)
        self.actionContour_filled.setObjectName(u"actionContour_filled")
        self.actionClearFig = QAction(MainWindow)
        self.actionClearFig.setObjectName(u"actionClearFig")
        self.actionWrite_ASCII = QAction(MainWindow)
        self.actionWrite_ASCII.setObjectName(u"actionWrite_ASCII")
        self.actionAdd = QAction(MainWindow)
        self.actionAdd.setObjectName(u"actionAdd")
        self.actionSubtract = QAction(MainWindow)
        self.actionSubtract.setObjectName(u"actionSubtract")
        self.actionMultiply = QAction(MainWindow)
        self.actionMultiply.setObjectName(u"actionMultiply")
        self.actionDivide = QAction(MainWindow)
        self.actionDivide.setObjectName(u"actionDivide")
        self.actionChop = QAction(MainWindow)
        self.actionChop.setObjectName(u"actionChop")
        self.actionIntegrate = QAction(MainWindow)
        self.actionIntegrate.setObjectName(u"actionIntegrate")
        self.actionDf_dt = QAction(MainWindow)
        self.actionDf_dt.setObjectName(u"actionDf_dt")
        self.actionSmooth = QAction(MainWindow)
        self.actionSmooth.setObjectName(u"actionSmooth")
        self.actionLow_pass_filter = QAction(MainWindow)
        self.actionLow_pass_filter.setObjectName(u"actionLow_pass_filter")
        self.actionHigh_pass_filter = QAction(MainWindow)
        self.actionHigh_pass_filter.setObjectName(u"actionHigh_pass_filter")
        self.actionBand_pass_filter = QAction(MainWindow)
        self.actionBand_pass_filter.setObjectName(u"actionBand_pass_filter")
        self.actionFFTP = QAction(MainWindow)
        self.actionFFTP.setObjectName(u"actionFFTP")
        self.actionRunFFT = QAction(MainWindow)
        self.actionRunFFT.setObjectName(u"actionRunFFT")
        self.actionReciprocal = QAction(MainWindow)
        self.actionReciprocal.setObjectName(u"actionReciprocal")
        self.actionExponential = QAction(MainWindow)
        self.actionExponential.setObjectName(u"actionExponential")
        self.actionAbsolute = QAction(MainWindow)
        self.actionAbsolute.setObjectName(u"actionAbsolute")
        self.actionArctan = QAction(MainWindow)
        self.actionArctan.setObjectName(u"actionArctan")
        self.actionNlog = QAction(MainWindow)
        self.actionNlog.setObjectName(u"actionNlog")
        self.actionNorm = QAction(MainWindow)
        self.actionNorm.setObjectName(u"actionNorm")
        self.actionInvert = QAction(MainWindow)
        self.actionInvert.setObjectName(u"actionInvert")
        self.actionAddCon = QAction(MainWindow)
        self.actionAddCon.setObjectName(u"actionAddCon")
        self.actionSubCon = QAction(MainWindow)
        self.actionSubCon.setObjectName(u"actionSubCon")
        self.actionMulCon = QAction(MainWindow)
        self.actionMulCon.setObjectName(u"actionMulCon")
        self.actionDivCon = QAction(MainWindow)
        self.actionDivCon.setObjectName(u"actionDivCon")
        self.actionPowCon = QAction(MainWindow)
        self.actionPowCon.setObjectName(u"actionPowCon")
        self.actionChangeName = QAction(MainWindow)
        self.actionChangeName.setObjectName(u"actionChangeName")
        self.actionChangeUnits = QAction(MainWindow)
        self.actionChangeUnits.setObjectName(u"actionChangeUnits")
        self.actionClip = QAction(MainWindow)
        self.actionClip.setObjectName(u"actionClip")
        self.actionStats = QAction(MainWindow)
        self.actionStats.setObjectName(u"actionStats")
        self.actionTimeOff = QAction(MainWindow)
        self.actionTimeOff.setObjectName(u"actionTimeOff")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionDeleteTrace = QAction(MainWindow)
        self.actionDeleteTrace.setObjectName(u"actionDeleteTrace")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.sourceTab = QWidget()
        self.sourceTab.setObjectName(u"sourceTab")
        self.gridLayout_3 = QGridLayout(self.sourceTab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.shotLabel = QLabel(self.sourceTab)
        self.shotLabel.setObjectName(u"shotLabel")

        self.gridLayout.addWidget(self.shotLabel, 0, 0, 1, 1)

        self.lastShotButton = QPushButton(self.sourceTab)
        self.lastShotButton.setObjectName(u"lastShotButton")

        self.gridLayout.addWidget(self.lastShotButton, 0, 4, 1, 1)

        self.tracePattern = QLineEdit(self.sourceTab)
        self.tracePattern.setObjectName(u"tracePattern")

        self.gridLayout.addWidget(self.tracePattern, 0, 7, 1, 1)

        self.availableSignals = QCheckBox(self.sourceTab)
        self.availableSignals.setObjectName(u"availableSignals")

        self.gridLayout.addWidget(self.availableSignals, 0, 9, 1, 1)

        self.readDataButton = QPushButton(self.sourceTab)
        self.readDataButton.setObjectName(u"readDataButton")

        self.gridLayout.addWidget(self.readDataButton, 0, 3, 1, 1)

        self.shotInput = QLineEdit(self.sourceTab)
        self.shotInput.setObjectName(u"shotInput")

        self.gridLayout.addWidget(self.shotInput, 0, 1, 1, 1)

        self.sourceDescription = QCheckBox(self.sourceTab)
        self.sourceDescription.setObjectName(u"sourceDescription")

        self.gridLayout.addWidget(self.sourceDescription, 0, 8, 1, 1)

        self.traceLabel = QLabel(self.sourceTab)
        self.traceLabel.setObjectName(u"traceLabel")

        self.gridLayout.addWidget(self.traceLabel, 0, 6, 1, 1)

        self.getAvailableSignalsButton = QPushButton(self.sourceTab)
        self.getAvailableSignalsButton.setObjectName(u"getAvailableSignalsButton")

        self.gridLayout.addWidget(self.getAvailableSignalsButton, 0, 2, 1, 1)

        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.splitter = QSplitter(self.sourceTab)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.treeView = QTreeWidget(self.splitter)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"Source")
        self.treeView.setHeaderItem(__qtreewidgetitem)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setColumnCount(1)
        self.splitter.addWidget(self.treeView)
        self.treeView.header().setVisible(False)
        self.treeView.header().setDefaultSectionSize(200)
        self.treeView.header().setStretchLastSection(True)
        self.sourceTable = QTableWidget(self.splitter)
        if self.sourceTable.columnCount() < 1:
            self.sourceTable.setColumnCount(1)
        self.sourceTable.setObjectName(u"sourceTable")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sourceTable.sizePolicy().hasHeightForWidth())
        self.sourceTable.setSizePolicy(sizePolicy)
        self.sourceTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sourceTable.setAlternatingRowColors(True)
        self.sourceTable.setSelectionMode(QAbstractItemView.MultiSelection)
        self.sourceTable.setShowGrid(True)
        self.sourceTable.setColumnCount(1)
        self.splitter.addWidget(self.sourceTable)
        self.sourceTable.horizontalHeader().setVisible(False)
        self.sourceTable.horizontalHeader().setDefaultSectionSize(200)
        self.sourceTable.horizontalHeader().setStretchLastSection(False)
        self.sourceTable.verticalHeader().setVisible(False)
        self.sourceTable.verticalHeader().setDefaultSectionSize(29)

        self.gridLayout_3.addWidget(self.splitter, 1, 0, 1, 1)

        self.tabWidget.addTab(self.sourceTab, "")
        self.dataTab = QWidget()
        self.dataTab.setObjectName(u"dataTab")
        self.gridLayout_5 = QGridLayout(self.dataTab)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.splitter_2 = QSplitter(self.dataTab)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Vertical)
        self.dataTable = QTableWidget(self.splitter_2)
        if self.dataTable.columnCount() < 4:
            self.dataTable.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.dataTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.dataTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.dataTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.dataTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.dataTable.setObjectName(u"dataTable")
        self.dataTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dataTable.setAlternatingRowColors(True)
        self.dataTable.setSelectionMode(QAbstractItemView.MultiSelection)
        self.dataTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dataTable.setShowGrid(False)
        self.dataTable.setGridStyle(Qt.SolidLine)
        self.splitter_2.addWidget(self.dataTable)
        self.dataTable.horizontalHeader().setStretchLastSection(True)
        self.dataTable.verticalHeader().setDefaultSectionSize(29)
        self.textOutput = QTextEdit(self.splitter_2)
        self.textOutput.setObjectName(u"textOutput")
        self.textOutput.setReadOnly(True)
        self.splitter_2.addWidget(self.textOutput)
        self.layoutWidget = QWidget(self.splitter_2)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.gridLayout_4 = QGridLayout(self.layoutWidget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)

        self.commandInput = ConsoleWidget(self.layoutWidget)
        self.commandInput.setObjectName(u"commandInput")

        self.gridLayout_4.addWidget(self.commandInput, 0, 1, 1, 1)

        self.commandButton = QPushButton(self.layoutWidget)
        self.commandButton.setObjectName(u"commandButton")

        self.gridLayout_4.addWidget(self.commandButton, 0, 2, 1, 1)

        self.splitter_2.addWidget(self.layoutWidget)

        self.gridLayout_5.addWidget(self.splitter_2, 0, 0, 1, 1)

        self.tabWidget.addTab(self.dataTab, "")
        self.plotTab = QWidget()
        self.plotTab.setObjectName(u"plotTab")
        self.tabWidget.addTab(self.plotTab, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1069, 29))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuAdd_source = QMenu(self.menuFile)
        self.menuAdd_source.setObjectName(u"menuAdd_source")
        self.menuPlot = QMenu(self.menubar)
        self.menuPlot.setObjectName(u"menuPlot")
        self.menuCommand = QMenu(self.menubar)
        self.menuCommand.setObjectName(u"menuCommand")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuPlot.menuAction())
        self.menubar.addAction(self.menuCommand.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.menuAdd_source.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoadState)
        self.menuFile.addAction(self.actionSaveState)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionWrite_ASCII)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuAdd_source.addAction(self.actionNetCDF_file)
        self.menuAdd_source.addAction(self.actionXPAD_tree)
        self.menuAdd_source.addAction(self.actionBOUT_data)
        self.menuPlot.addAction(self.actionPlot)
        self.menuPlot.addAction(self.actionOPlot)
        self.menuPlot.addAction(self.actionMPlot)
        self.menuPlot.addAction(self.actionZPlot)
        self.menuPlot.addAction(self.actionXYPlot)
        self.menuPlot.addAction(self.actionContour)
        self.menuPlot.addAction(self.actionContour_filled)
        self.menuPlot.addAction(self.actionClearFig)
        self.menuCommand.addAction(self.actionDeleteTrace)
        self.menuCommand.addSeparator()
        self.menuCommand.addAction(self.actionChop)
        self.menuCommand.addSeparator()
        self.menuCommand.addAction(self.actionIntegrate)
        self.menuCommand.addAction(self.actionDf_dt)
        self.menuCommand.addAction(self.actionSmooth)
        self.menuCommand.addAction(self.actionBand_pass_filter)
        self.menuCommand.addSeparator()
        self.menuCommand.addAction(self.actionAdd)
        self.menuCommand.addAction(self.actionSubtract)
        self.menuCommand.addAction(self.actionMultiply)
        self.menuCommand.addAction(self.actionDivide)
        self.menuCommand.addSeparator()
        self.menuCommand.addAction(self.actionFFTP)
        self.menuCommand.addAction(self.actionRunFFT)
        self.menuCommand.addSeparator()
        self.menuCommand.addAction(self.actionReciprocal)
        self.menuCommand.addAction(self.actionExponential)
        self.menuCommand.addAction(self.actionAbsolute)
        self.menuCommand.addAction(self.actionArctan)
        self.menuCommand.addAction(self.actionNlog)
        self.menuCommand.addAction(self.actionNorm)
        self.menuCommand.addAction(self.actionInvert)
        self.menuCommand.addAction(self.actionAddCon)
        self.menuCommand.addAction(self.actionSubCon)
        self.menuCommand.addAction(self.actionMulCon)
        self.menuCommand.addAction(self.actionDivCon)
        self.menuCommand.addAction(self.actionPowCon)
        self.menuCommand.addAction(self.actionChangeName)
        self.menuCommand.addAction(self.actionChangeUnits)
        self.menuCommand.addAction(self.actionClip)
        self.menuCommand.addAction(self.actionStats)
        self.menuCommand.addAction(self.actionTimeOff)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", u"PyXPad", None)
        )
        self.actionLoadState.setText(
            QCoreApplication.translate("MainWindow", u"&Load state", None)
        )
        self.actionSaveState.setText(
            QCoreApplication.translate("MainWindow", u"&Save state", None)
        )
        self.actionExit.setText(
            QCoreApplication.translate("MainWindow", u"E&xit", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionExit.setToolTip(
            QCoreApplication.translate("MainWindow", u"Exit pyXpad", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+Q", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionXPAD_tree.setText(
            QCoreApplication.translate("MainWindow", u"XPAD tree", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionXPAD_tree.setToolTip(
            QCoreApplication.translate("MainWindow", u"Load a tree of XPAD items", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.actionNetCDF_file.setText(
            QCoreApplication.translate("MainWindow", u"NetCDF file", None)
        )
        self.actionPlot.setText(
            QCoreApplication.translate("MainWindow", u"&Plot", None)
        )
        self.actionOPlot.setText(
            QCoreApplication.translate("MainWindow", u"&OPlot", None)
        )
        self.actionMPlot.setText(
            QCoreApplication.translate("MainWindow", u"&MPlot", None)
        )
        self.actionXYPlot.setText(
            QCoreApplication.translate("MainWindow", u"&XYPlot", None)
        )
        self.actionZPlot.setText(
            QCoreApplication.translate("MainWindow", u"&ZPlot", None)
        )
        self.actionBOUT_data.setText(
            QCoreApplication.translate("MainWindow", u"BOUT++ data", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionBOUT_data.setToolTip(
            QCoreApplication.translate(
                "MainWindow", u"Read BOUT++ data directory", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionBOUT_data.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+S", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionContour.setText(
            QCoreApplication.translate("MainWindow", u"&Contour", None)
        )
        self.actionContour_filled.setText(
            QCoreApplication.translate("MainWindow", u"Contour &filled", None)
        )
        self.actionClearFig.setText(
            QCoreApplication.translate("MainWindow", u"C&lear Figure", None)
        )
        self.actionWrite_ASCII.setText(
            QCoreApplication.translate("MainWindow", u"&Write ASCII", None)
        )
        self.actionAdd.setText(
            QCoreApplication.translate("MainWindow", u"X+Y (Sum Channels)", None)
        )
        self.actionSubtract.setText(
            QCoreApplication.translate("MainWindow", u"X-Y", None)
        )
        self.actionMultiply.setText(
            QCoreApplication.translate("MainWindow", u"X*Y", None)
        )
        self.actionDivide.setText(
            QCoreApplication.translate("MainWindow", u"X/Y", None)
        )
        self.actionChop.setText(QCoreApplication.translate("MainWindow", u"Chop", None))
        self.actionIntegrate.setText(
            QCoreApplication.translate("MainWindow", u"Integrate", None)
        )
        self.actionDf_dt.setText(
            QCoreApplication.translate("MainWindow", u"df/dt", None)
        )
        self.actionSmooth.setText(
            QCoreApplication.translate("MainWindow", u"Smooth", None)
        )
        self.actionLow_pass_filter.setText(
            QCoreApplication.translate("MainWindow", u"Low pass filter", None)
        )
        self.actionHigh_pass_filter.setText(
            QCoreApplication.translate("MainWindow", u"High pass filter", None)
        )
        self.actionBand_pass_filter.setText(
            QCoreApplication.translate("MainWindow", u"Band pass filter", None)
        )
        self.actionFFTP.setText(QCoreApplication.translate("MainWindow", u"FFTP", None))
        self.actionRunFFT.setText(
            QCoreApplication.translate("MainWindow", u"Running FFT", None)
        )
        self.actionReciprocal.setText(
            QCoreApplication.translate("MainWindow", u"1/X", None)
        )
        self.actionExponential.setText(
            QCoreApplication.translate("MainWindow", u"exp", None)
        )
        self.actionAbsolute.setText(
            QCoreApplication.translate("MainWindow", u"abs", None)
        )
        self.actionArctan.setText(
            QCoreApplication.translate("MainWindow", u"arctan", None)
        )
        self.actionNlog.setText(QCoreApplication.translate("MainWindow", u"ln", None))
        self.actionNorm.setText(
            QCoreApplication.translate("MainWindow", u"Normalise", None)
        )
        self.actionInvert.setText(
            QCoreApplication.translate("MainWindow", u"Invert", None)
        )
        self.actionAddCon.setText(
            QCoreApplication.translate("MainWindow", u"X+C", None)
        )
        self.actionSubCon.setText(
            QCoreApplication.translate("MainWindow", u"X-C", None)
        )
        self.actionMulCon.setText(
            QCoreApplication.translate("MainWindow", u"X*C", None)
        )
        self.actionDivCon.setText(
            QCoreApplication.translate("MainWindow", u"X/C", None)
        )
        self.actionPowCon.setText(
            QCoreApplication.translate("MainWindow", u"X^C", None)
        )
        self.actionChangeName.setText(
            QCoreApplication.translate("MainWindow", u"Change Name", None)
        )
        self.actionChangeUnits.setText(
            QCoreApplication.translate("MainWindow", u"Change Units", None)
        )
        self.actionClip.setText(QCoreApplication.translate("MainWindow", u"Clip", None))
        self.actionStats.setText(
            QCoreApplication.translate("MainWindow", u"Statistics", None)
        )
        self.actionTimeOff.setText(
            QCoreApplication.translate("MainWindow", u"Time Offset", None)
        )
        self.actionAbout.setText(
            QCoreApplication.translate("MainWindow", u"&About", None)
        )
        self.actionDeleteTrace.setText(
            QCoreApplication.translate("MainWindow", u"&Delete Trace", None)
        )
        self.shotLabel.setText(QCoreApplication.translate("MainWindow", u"Shot:", None))
        # if QT_CONFIG(tooltip)
        self.lastShotButton.setToolTip(
            QCoreApplication.translate("MainWindow", u"Get last shot number", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.lastShotButton.setText(
            QCoreApplication.translate("MainWindow", u"&Last shot", None)
        )
        self.tracePattern.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow", u"Filter traces with wildcards", None
            )
        )
        self.availableSignals.setText(
            QCoreApplication.translate(
                "MainWindow", u"Show available signals only", None
            )
        )
        self.readDataButton.setText(
            QCoreApplication.translate("MainWindow", u"&Read", None)
        )
        self.sourceDescription.setText(
            QCoreApplication.translate("MainWindow", u"Show description", None)
        )
        self.traceLabel.setText(
            QCoreApplication.translate("MainWindow", u"Trace:", None)
        )
        self.getAvailableSignalsButton.setText(
            QCoreApplication.translate("MainWindow", u"Get signals", None)
        )
        # if QT_CONFIG(tooltip)
        self.sourceTable.setToolTip(
            QCoreApplication.translate("MainWindow", u"List of available signals", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.sourceTab),
            QCoreApplication.translate("MainWindow", u"&Sources", None),
        )
        ___qtablewidgetitem = self.dataTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("MainWindow", u"Name", None)
        )
        ___qtablewidgetitem1 = self.dataTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("MainWindow", u"Source", None)
        )
        ___qtablewidgetitem2 = self.dataTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("MainWindow", u"Trace", None)
        )
        ___qtablewidgetitem3 = self.dataTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate("MainWindow", u"Comments", None)
        )
        self.label_3.setText(
            QCoreApplication.translate("MainWindow", u"Command:", None)
        )
        self.commandButton.setText(
            QCoreApplication.translate("MainWindow", u"Run", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.dataTab),
            QCoreApplication.translate("MainWindow", u"&Data", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.plotTab),
            QCoreApplication.translate("MainWindow", u"&Plot", None),
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menuAdd_source.setTitle(
            QCoreApplication.translate("MainWindow", u"&Add source", None)
        )
        self.menuPlot.setTitle(
            QCoreApplication.translate("MainWindow", u"&Graphics", None)
        )
        self.menuCommand.setTitle(
            QCoreApplication.translate("MainWindow", u"&Command", None)
        )
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))

    # retranslateUi
