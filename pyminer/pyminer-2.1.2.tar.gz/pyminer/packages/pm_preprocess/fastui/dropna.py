"""
这是一个去除缺失值的面板

运行方式：运行PyMiner后，直接运行此文件即可。
需要确保PyMiner的工作空间中有pandas.DataFrame类型的数据。

# -*- coding:utf-8 -*-
# @Time: 2021/2/7 21:00
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: datamerge.py
"""
from PySide2.QtWidgets import QApplication

if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog


class DropNADialog(DFOperationDialog):
    def __init__(self, ):
        super(DropNADialog, self).__init__()
        views = [
            ('combo_ctrl', 'axis', self.tr('去除方向'), 0, [0, 1], [self.tr('行'), self.tr('列')]),
            ('combo_ctrl', 'how', self.tr('去除标准'), 'any', ['all', 'any'], [self.tr('该行/列数据全为缺失值'),
                                                                           self.tr('该行/列任一数据为缺失值')]),
            ('numberspin_ctrl', 'thresh', '保留非空值多于等于此的行/列', 1, '', (0, 1000), 1),
            ('check_ctrl', 'use_subset', self.tr('按行列筛选'), False),
            ('list_ctrl', 'subset', self.tr('筛选目标列'), [[], [], ], lambda: None),
        ]
        self.panel.set_items(views)
        self.panel.set_as_controller('how', ['thresh'], 'all', 'enable')
        self.panel.set_as_controller('use_subset', ['subset'], True, 'enable')

    def get_prompt_template(self) -> str:
        return self.tr('Drop NA:')

    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()
        varname = self.combo_box.currentText()
        use_subset = values.pop('use_subset')

        code = '{varname}.dropna({args_str})'. \
            format(varname=varname, args_str=self.kwargs_to_str(values))
        return code


if __name__ == '__main__':
    app = QApplication([])
    md = DropNADialog()
    md.show()
    app.exec_()
