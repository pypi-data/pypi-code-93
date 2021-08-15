import os
import sys
import logging
import datetime
import webbrowser
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_float_dtype
from pandas.api.types import is_string_dtype

from PySide2.QtWidgets import QWidget, QDesktopWidget, QApplication, QComboBox
from PySide2.QtCore import Qt
# 导入数据相关操作模块
from packages.pm_preprocess.ui.data_filter import Ui_Form as DataFilter_Ui_Form  # 数据筛选
from packages.pm_preprocess.base import BaseDataPreprocessForm
from utils import bind_combo_with_workspace


class DataFilterForm(BaseDataPreprocessForm, DataFilter_Ui_Form):
    """
    打开"数据-筛选"窗口
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.center()
        # self.bind_events()




if __name__ == '__main__':
    import cgitb
    cgitb.enable()
    app = QApplication(sys.argv)
    form = DataFilterForm()
    form.show()
    sys.exit(app.exec_())
