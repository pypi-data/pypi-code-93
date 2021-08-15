"""
导入数据对话框的基类。
包含：获取帮助；按esc退出；自动窗体置中等。
使用方法见datamissingvalue.py中的继承。
class DataMissingValueForm(BaseDataPreprocessForm, DataMissingValue_Ui_Form):

统一控件：
combo_var_name:QComboBox，选择变量用。
pushButton_code:QPushButton，点击显示代码
pushButton_ok:QPushButton,点击确认
pushButton_save:QPushButton,点击保存
pushButton_cancel:QPushButton，点击取消
pushButton_help:QPushButton，点击获取帮助

这些按钮需要默认所有的dialog都有！在setup_ui方法之后进行初始化，连接信号和槽。也就是bind_events方法。

统一方法：
save(self)(保存，界面不退出)
ok(self):点击确认退出。也就是是调用save和close
cancel(self):点击退出按钮或者按esc触发。
dataset_name_changed(self):变量名改变时触发的方法
get_current_dataset_name(self):获取当前变量名
get_current_dataset(self):获取当前的数据集


dataset_update(self,dataset_name,dataset):将名为dataset_name的dataset写回工作空间。如果有重名，将弹框修改，直至输入不冲突的变量名为止。

"""
import logging
import webbrowser
import datetime

from PySide2.QtWidgets import QWidget, QDesktopWidget, QDialog, QInputDialog, QLineEdit, QMessageBox, QPushButton, \
    QComboBox
from PySide2.QtCore import Qt, Signal
from utils import input_identifier, bind_combo_with_workspace
from pyminer_comm import set_var, get_var
import pandas as pd


class BaseDataPreprocessForm(QDialog):
    """
    窗口基类
    """
    signal_data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.combo_var_name: QComboBox = None
        self.pushButton_code: QPushButton = None
        self.pushButton_ok: QPushButton = None
        self.pushButton_save: QPushButton = None
        self.pushButton_cancel: QPushButton = None
        self.pushButton_help: QPushButton = None

    def bind_events(self):
        """
        连接事件。
        :return:
        """
        if isinstance(self.pushButton_ok, QPushButton):
            self.pushButton_ok.clicked.connect(self.ok)
        if isinstance(self.pushButton_save, QPushButton):
            self.pushButton_save.clicked.connect(self.save)
        if isinstance(self.pushButton_help, QPushButton):
            self.pushButton_help.clicked.connect(self.get_help)
        if isinstance(self.pushButton_cancel, QPushButton):
            self.pushButton_cancel.clicked.connect(self.cancel)
        if isinstance(self.combo_var_name, QComboBox):
            bind_combo_with_workspace(self.combo_var_name, type_filter='table')
            self.combo_var_name.currentIndexChanged.connect(self.dataset_name_changed)

    def keyPressEvent(self, e):
        """
        按键盘Escape退出当前窗口
        @param e:
        """
        if e.key() == Qt.Key_Escape:
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

    def dataset_update(self, name: str, dataset):
        reply = QMessageBox.information(self, "注意", "是否保存当前筛选结果到工作区间并覆盖原数据", QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)
        if reply == QMessageBox.Yes:
            if len(dataset) > 0:
                set_var(name, dataset)
        else:
            dataset_name = input_identifier(self, name)
            print(dataset_name)
            if dataset_name != '':
                set_var(dataset_name, dataset)

    def ok(self):
        pass

    def cancel(self):
        self.close()

    def save(self):
        pass

    def get_current_dataset_name(self) -> str:
        return self.combo_var_name.currentText()

    def get_current_dataset(self) -> pd.DataFrame:
        name = self.get_current_dataset_name()
        if name.isidentifier():
            return get_var(name)
        else:
            return None

    def dataset_name_changed(self):
        pass
