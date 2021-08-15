# -*- coding:utf-8 -*-
# @Time: 2021/2/7 21:00
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: datamerge.py


# DataFrame.fillna(value=None, method=None, axis=None, inplace=False, limit=None, downcast=None, **kwargs)
# value: 变量、字典、Series，DataFrame；用于填充缺失值，或指定为每个索引（对于Series）或列（对于DataFrame）的缺失值使用字典/Series/DataFrame的值填充
# method: {'backfill', 'bfill', 'pad', 'ffill', None}, 默认None， pad/ffill表示向后填充空值，backfill/bfill表示向前填充空值
# axis: {0 or 'index', 1 or 'columns'}
# inplace: boolean, 默认为False。若为True， 在原地填满
# limit: int, 默认为None， 如果指定了方法， 则这是连续的NaN值的前向/后向填充的最大数量
# downcast: dict, 默认None， 字典中的项为类型向下转换规则。

# 以上有关函数名称的解释来源于简书。
# 作者：KissedbyFire
# 链接：https://www.jianshu.com/p/17cb2733a6d7


from typing import List

from pmgwidgets import PMGPanelDialog, PMGPanel
from pyminer_comm.base import is_pyminer_service_started
from pyminer_comm import get_var_names, get_var, set_var, run_command
from utils import VariableSelect, input_identifier
from PySide2.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QSpinBox, QApplication, QMessageBox, QPushButton

if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog




class FillNADialog(DFOperationDialog):
    def __init__(self, ):
        super(FillNADialog, self).__init__()
        views = [
            ('combo_ctrl', 'replace_policy', self.tr('Replace Policy'), 1, [0, 1],
             [self.tr('User Defined Value'), self.tr('Fill Front or Back')]),
            ('line_ctrl', 'value', self.tr('Value to replace'), ''),
            ('combo_ctrl', 'method', self.tr('Fill Direction'), 'ffill', ['ffill', 'bfill'],
             [self.tr('Front Fill'), self.tr('Back Fill')]),
            ('combo_ctrl', 'axis', self.tr('Fill Axis'), 0, [0, 1], [self.tr('By Row'),
                                                                     self.tr('By Column')]),

            ('check_ctrl', 'with_limit', self.tr('Limit Maximum Fills'), True),
            ('numberspin_ctrl', 'limit', self.tr('Maximum Fills'), 1, '', (0, 1000), 1),
            ('check_ctrl', 'inplace', self.tr('In Place'), False),
        ]
        self.panel.set_items(views)
        self.panel.set_as_controller('replace_policy', ['value'], 0, 'enable')
        self.panel.set_as_controller('replace_policy', ['method', 'axis'], 1, 'enable')
        self.panel.set_as_controller('with_limit', ['limit'], True, 'enable')

    def get_prompt_template(self) -> str:
        return self.tr('Fill NA:')

    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        varname = self.combo_box.currentText()
        policy = values.pop('replace_policy')
        with_limit = values.pop('with_limit')
        args_str = ''
        for k, v in values.items():
            args_str += '{k}={v},'.format(k=k, v=repr(v))
        code = '{varname}.fillna({args})'.format(varname=varname, args=args_str)
        return code


if __name__ == '__main__':
    app = QApplication([])
    md = FillNADialog()
    md.show()
    app.exec_()
