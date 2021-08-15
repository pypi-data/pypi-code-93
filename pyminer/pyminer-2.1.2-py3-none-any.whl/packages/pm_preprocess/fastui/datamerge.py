"""
这个文件是用代码生成方式构建图形化应用的一个示例。
继承：BaseOperationDialog
其中的方法：


"""
# -*- coding:utf-8 -*-
# @Time: 2021/2/7 21:00
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: datamerge.py

from typing import List

from pmgwidgets import PMGPanelDialog, PMGPanel, PMGOneShotThreadRunner
from pyminer_comm.base import is_pyminer_service_started
from pyminer_comm import get_var_names, get_var, set_var, run_command, call_interface
from utils import VariableSelect, input_identifier
from PySide2.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QSpinBox, QApplication, QMessageBox, QPushButton

if not __name__ == '__main__':
    from .base import BaseOperationDialog
else:
    from base import BaseOperationDialog


class MergeDialog(BaseOperationDialog):
    def __init__(self, axis: int):
        super(MergeDialog, self).__init__()
        self.setLayout(QVBoxLayout())
        self.panel = PMGPanel()
        self.axis = axis
        self.button_box = QDialogButtonBox()
        self.button_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.close)
        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(6)
        self.layout().addWidget(self.spin_box)
        self.layout().addWidget(self.panel)
        self.layout().addWidget(self.button_box)
        self.spin_box.valueChanged.connect(self.on_spinbox_value_changed)
        self.spin_box.setValue(2)

        self.thrunner: PMGOneShotThreadRunner = None

    def on_spinbox_value_changed(self):
        if self.spin_box.value() > 6:
            QMessageBox.warning(self, self.tr('Warning'), self.tr('You can merge at most 6 data frames.'))
            return
        if not is_pyminer_service_started():
            names = ['a', 'b', 'c', 'd']
            name = 'a'
        else:
            names = get_var_names()

            if len(names) == 0:
                QMessageBox.warning(self, self.tr('Warning'), self.tr('No Data found in workspace!'))
                return
            else:
                name = names[0]
        items = [('combo_ctrl', 'dataset#%d' % i, '第%d个数据' % (i + 1), name, names) for i in
                 range(self.spin_box.value())]
        self.panel.set_items(items)

    def accept(self) -> None:
        """
        点击Ok时触发的事件
        Returns:

        """
        identifier = input_identifier(self, 'merged_df')
        if identifier != '':
            code = identifier + '=' + self.get_value_code()
            run_command(code, self.tr('Import Data, code: %s') % code, False)

    def get_args(self) -> str:
        """
        获取函数的参数
        Returns:

        """
        names = ''
        for k, name in self.panel.get_value().items():
            names += name + ','
        return '[' + names + '], {axis}'.format(axis=repr(self.axis))

    def get_value_code(self) -> str:
        """
        获取代码
        Returns:

        """
        return 'pd.concat(%s)' % self.get_args()

    def on_update_vars(self, vars: List[str]):
        """

        Args:
            vars:

        Returns:

        """
        if len(vars) < 2:
            return
        if len(vars) > 6:
            vars = vars[:6]
        self.spin_box.setValue(len(vars))
        print(vars)
        items = [('combo_ctrl', 'dataset#%d' % i, '第%d个数据' % (i + 1), vars[i], vars) for i in
                 range(self.spin_box.value())]
        self.panel.set_items(items)
        # self.combo_box.setCurrentText(vars[0])


if __name__ == '__main__':
    app = QApplication([])
    md = MergeDialog(0)
    md.show()
    app.exec_()
    # items = [('combo_ctrl','dataset_a')]
    # self.panel.set_items()
