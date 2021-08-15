# -*- coding:utf-8 -*-
# @Time: 2021/2/8 13:01
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: template.py.py

# -*- coding:utf-8 -*-
# @Time: 2021/2/7 21:00
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: datamerge.py
code = """
from typing import List

from pmgwidgets import PMGPanelDialog, PMGPanel
from pyminer_comm.base import is_pyminer_service_started
from pyminer_comm import get_var_names, get_var, set_var, run_command
from pmtoolbox import VariableSelect, input_identifier
from PySide2.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QSpinBox, QApplication, QMessageBox, QPushButton,QComboBox


class CLASS_NAME(QDialog):
    def __init__(self, ):
        super(CLASS_NAME, self).__init__()
        self.setLayout(QVBoxLayout())
        names = get_var_names()
        if len(names) == 0:
            QMessageBox.warning(self, self.tr('Warning'), self.tr('No data in workspace'))
            self.close()
            return
        self.combo_box = QComboBox()
        self.combo_box.addItems(names)
        self.combo_box.setCurrentIndex(0)
        views = %s
        self.panel = PMGPanel(views=views)
%s
        
        self.button_box = QDialogButtonBox()
        self.button_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Help)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.close)

        self.layout().addWidget(self.panel)
        self.layout().addWidget(self.button_box)

    def accept(self) -> None:

        code = self.get_code()
        if code != '':
            run_command(command=code, hint_text='Drop NA, command: ' + code, hidden=False)
            super().accept()

    def get_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        varname = self.combo_box.currentText()
%s
        args_str = ''
        for k, v in values.items():
            args_str += '{k}={v},'.format(k=k, v=repr(v))
        return '{varname}.fillna({args})'.format(varname=varname, args=args_str)

        if not values['inplace']:
            identifier = input_identifier(parent=self, default_name=varname)
            if identifier != '':
                code = identifier + ' = ' + code
            else:
                return ''
        return code


if __name__ == '__main__':
    app = QApplication([])
    md = CLASS_NAME()
    md.show()
    app.exec_()
"""
# print(code)
import json

with open('dropna.json', 'rb') as f:
    d = json.load(f)
params = repr(d['params'])
rule_widgets = d['rule_widgets']
pop_rule_widgets_setence = ''
for w_name in rule_widgets:
    pop_rule_widgets_setence += '        values.pop(\'%s\')\n' % w_name
# print(params)

show_rules_setence = ''
for rule in d['rules']:
    r = ''
    print(rule)
    for text in rule:
        r += repr(text) + ','
    show_rules_setence += '        self.panel.set_as_controller(%s)\n' % r

code = code % (params, show_rules_setence, pop_rule_widgets_setence)
print(code)
# exec(code)
with open(d['file_name'], 'w', encoding='utf8') as f:
    f.write(code)
