import datetime
import sys
import webbrowser
import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_numeric_dtype
from PySide2.QtCore import QSize, Qt, Signal
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QHBoxLayout, QWidget, QSpacerItem, QToolButton, QSizePolicy, QWizard, QMessageBox, \
    QFileDialog, QFrame, QDesktopWidget, QDialog, QTableWidgetItem, QInputDialog, QAbstractItemView, QLineEdit, \
    QApplication, QTableWidget

# 导入数据相关操作模块
from packages.pm_statistics.ui.stat_base import Ui_Form as StatDesc_Ui_Form  # 数据统计
from packages.pm_statistics.describe import set_stats


class StatDescForm(QDialog, StatDesc_Ui_Form):
    """
    打开"统计-描述统计"窗口
    """
    signal_data_change = Signal(str, dict)  # 自定义信号，用于修改数据 变量名，数据集

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.center()

        # 变量初始化
        self.stat_items = ['Name','Total Count', 'N', 'N*', '% Missing', 'Min', '25%',
                           'Median', '75%', 'Max', 'Mean', 'Std']
        self.current_dataset = pd.DataFrame()  # 当前数据集
        self.selected_var = []  # 已选变量
        self.precision = 2  # 数据精度

        # test
        self.current_dataset = pd.read_csv("d:/demo/class.csv")

        x = 0
        for i in self.current_dataset.columns:
            self.listWidget_selected.insertItem(x, i)
            ++x
        self.set_selected_var()

        #  绑定事件
        self.listWidget_selected.itemChanged.connect(self.set_selected_var)
        self.pushButton_ok.clicked.connect(self.dataset_stat)
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton_help.clicked.connect(self.get_help)

        self.spinBox_precision.valueChanged.connect(self.set_precision)
        self.radioButton_all.toggled.connect(self.stat_items_change)
        self.radioButton_custom.toggled.connect(self.stat_item_change)
        self.checkBox_total_cnt.stateChanged.connect(self.stat_item_change)
        self.checkBox_valid_cnt.stateChanged.connect(self.stat_item_change)
        self.checkBox_valid_ratio.stateChanged.connect(self.stat_item_change)
        self.checkBox_miss_cnt.stateChanged.connect(self.stat_item_change)
        self.checkBox_miss_ratio.stateChanged.connect(self.stat_item_change)
        self.checkBox_unique.stateChanged.connect(self.stat_item_change)
        self.checkBox_max.stateChanged.connect(self.stat_item_change)
        self.checkBox_min.stateChanged.connect(self.stat_item_change)

        self.checkBox_sum.stateChanged.connect(self.stat_item_change)
        self.checkBox_mean.stateChanged.connect(self.stat_item_change)
        self.checkBox_mode.stateChanged.connect(self.stat_item_change)
        self.checkBox_kurt.stateChanged.connect(self.stat_item_change)
        self.checkBox_skew.stateChanged.connect(self.stat_item_change)
        self.checkBox_var.stateChanged.connect(self.stat_item_change)
        self.checkBox_std.stateChanged.connect(self.stat_item_change)
        self.checkBox_se_mean.stateChanged.connect(self.stat_item_change)

        self.checkBox_q1.stateChanged.connect(self.stat_item_change)
        self.checkBox_median.stateChanged.connect(self.stat_item_change)
        self.checkBox_q3.stateChanged.connect(self.stat_item_change)
        self.checkBox_qrange.stateChanged.connect(self.stat_item_change)
        self.checkBox_range.stateChanged.connect(self.stat_item_change)
        self.checkBox_cv.stateChanged.connect(self.stat_item_change)
        self.checkBox_sum_of_squares.stateChanged.connect(self.stat_item_change)

    def keyPressEvent(self, e):
        """
        按键盘Escape退出当前窗口
        @param e:
        """
        if e.key() == Qt.Key_Escape:
            reply = QMessageBox.question(self, '确认退出？', '是否退出当前窗口？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.close()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def get_help(self):
        """
        打开帮助页面
        """
        try:
            webbrowser.get('chrome').open_new_tab("http://www.pyminer.com")
        except Exception as e:
            webbrowser.open_new_tab("http://www.pyminer.com")

    def set_precision(self):
        """
        设置统计结果的数据精度
        Returns:
            数据精度，即需要保留的小数点位数
        """
        self.precision = self.spinBox_precision.value()

    def set_selected_var(self):
        self.selected_var = []
        count = self.listWidget_selected.count()
        txt = self.listWidget_selected.item(1).text()
        self.selected_var.append(txt)
        # for i in range(self.listWidget_selected.count()):
        #     print(i)
        #     self.selected_var.append()

    def stat_items_change(self):
        self.stat_items = ['Name','Total Count', 'N', 'N*', '% N', '% Missing', 'Unique', 'CumN', 'Sum', 'Min', '25%',
                           'Median', '75%', 'Max', 'Mean', 'Std', 'Var', 'CV', 'Range', 'QRange', 'Mode',
                           'Sum of squares', 'Skew', 'Kurt', 'MSSD']

    def stat_item_change(self):
        self.stat_items = []
        self.stat_items.append('Name')
        if self.checkBox_total_cnt.isChecked():
            self.stat_items.append('Total Count')
        if self.checkBox_valid_cnt.isChecked():
            self.stat_items.append('N')
        if self.checkBox_valid_ratio.isChecked():
            self.stat_items.append('% N')
        if self.checkBox_miss_cnt.isChecked():
            self.stat_items.append('N*')
        if self.checkBox_miss_ratio.isChecked():
            self.stat_items.append('% Missing')
        if self.checkBox_unique.isChecked():
            self.stat_items.append('Unique')
        if self.checkBox_max.isChecked():
            self.stat_items.append('Max')
        if self.checkBox_min.isChecked():
            self.stat_items.append('Min')
        if self.checkBox_sum.isChecked():
            self.stat_items.append('Sum')
        if self.checkBox_mean.isChecked():
            self.stat_items.append('Mean')
        if self.checkBox_mode.isChecked():
            self.stat_items.append('Mode')
        if self.checkBox_kurt.isChecked():
            self.stat_items.append('Kurt')
        if self.checkBox_skew.isChecked():
            self.stat_items.append('Skew')
        if self.checkBox_var.isChecked():
            self.stat_items.append('Var')
        if self.checkBox_std.isChecked():
            self.stat_items.append('Std')
        if self.checkBox_se_mean.isChecked():
            self.stat_items.append('SE Mean')
        if self.checkBox_q1.isChecked():
            self.stat_items.append('25%')
        if self.checkBox_median.isChecked():
            self.stat_items.append('Median')
        if self.checkBox_q3.isChecked():
            self.stat_items.append('75%')
        if self.checkBox_qrange.isChecked():
            self.stat_items.append('Qrange')
        if self.checkBox_range.isChecked():
            self.stat_items.append('Range')
        if self.checkBox_cv.isChecked():
            self.stat_items.append('CV')
        if self.checkBox_sum_of_squares.isChecked():
            self.stat_items.append('Sum of squares')

        print("统计指标:", self.stat_items)

    def dataset_stat(self):
        """
        根据已选的数据集、统计列、统计项、数据精度，返回描述统计结果
        Returns:

        """
        stat_df = self.current_dataset.loc[:, self.selected_var]
        result = set_stats(stat_df, self.stat_items, self.precision)
        self.show_table(result)

    def show_table(self, dataset):
        dialog = Stat_Dialog()
        tablewidget = dialog.tablewidget
        tablewidget.setRowCount(len(dataset))
        tablewidget.setColumnCount(len(dataset.columns))

        tablewidget.setHorizontalHeaderLabels(list(dataset.columns))
        tablewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #  将行与列的高度设置为所显示的内容的宽度高度匹配
        QTableWidget.resizeColumnsToContents(tablewidget)
        # QTableWidget.resizeRowsToContents(tablewidget)

        # 插入数据
        for i in range(len(dataset)):
            for j in range(len(dataset.columns)):
                text = dataset.iat[i, j]
                newItem = QTableWidgetItem(str(text))
                if type(text) == type('a'):
                    newItem.setTextAlignment(Qt.AlignLeft)
                else:
                    newItem.setTextAlignment(Qt.AlignRight)
                tablewidget.setItem(i, j, newItem)
        dialog.exec_()


class Stat_Dialog(QDialog):
    def __init__(self):
        super(Stat_Dialog, self).__init__()
        self.resize(800, 600)
        self.setWindowTitle("描述统计结果")

        layout = QHBoxLayout(self)
        self.tablewidget = QTableWidget()
        layout.addWidget(self.tablewidget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = StatDescForm()
    form.show()
    sys.exit(form.exec_())
