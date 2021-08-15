
from typing import List

from pmgwidgets import PMGPanelDialog, PMGPanel
from pyminer_comm.base import is_pyminer_service_started
from pyminer_comm import get_var_names, get_var, set_var, run_command
from utils import VariableSelect, input_identifier
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
        views = [['combo_ctrl', 'axis', 'Position', 0, [0, 1], ['行', '列']], ['combo_ctrl', 'how', 'How to drop', 'any', ['all', 'any'], ['All', 'Any']], ['numberspin_ctrl', 'thresh', '保留非空值多于等于此的行/列', 1, '', [0, 1000], 1], ['check_ctrl', 'use_subset', 'Drop by subset', True], ['list_ctrl', 'subset', 'Subset', [[], []], None], ['check_ctrl', 'inplace', 'In Place', False]]
        self.panel = PMGPanel(views=views)
        self.panel.set_as_controller('use_subset',['subset'],True,'enable',)
        self.panel.set_as_controller('how',['thresh'],'any','enable',)

        
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
        values.pop('use_subset')
        values.pop('number')

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
