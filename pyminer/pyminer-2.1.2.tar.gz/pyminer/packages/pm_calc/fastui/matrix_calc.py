from PySide2.QtWidgets import QApplication, QMessageBox

from pyminer_comm import get_var_names
from utils import bind_panel_combo_ctrl_with_workspace

if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog


class MatrixCalcDialog(DFOperationDialog):
    def __init__(self, ):
        super(MatrixCalcDialog, self).__init__()
        self.setWindowTitle("矩阵计算")
        self.combo_box.hide()
        self.hint_label.hide()
        names = get_var_names()

        if len(names) == 0:
            names = [self.no_var_in_workspace_hint()]
            name_A = self.no_var_in_workspace_hint()
            name_B = self.no_var_in_workspace_hint()
        else:
            name_A = names[0]
            name_B = names[-1]
        views = [
            ('combo_ctrl', 'calc_type', self.tr('计算类型'), "outer_product",
             ["inner_product", "outer_product", "add", "sub"],
             ['A·B', 'A×B', 'A+B', 'A-B']),
            ('combo_ctrl', 'A', 'A', name_A, names),
            ('combo_ctrl', 'B', 'B', name_B, names)
        ]
        self.panel.set_items(views)
        bind_panel_combo_ctrl_with_workspace(self.panel.get_ctrl("A"))
        bind_panel_combo_ctrl_with_workspace(self.panel.get_ctrl("B"))

    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        name_A = values["A"]
        name_B = values["B"]
        calc_type = values["calc_type"]
        args_str = ''
        func_name = ""
        if calc_type == "inner_product":
            func_name = 'np.multiply'
            return "{func_name}({name_A},{name_B})".format(func_name=func_name, name_A=name_A, name_B=name_B)
        elif calc_type == "outer_product":
            func_name = "np.dot"
            return "{func_name}({name_A},{name_B})".format(func_name=func_name, name_A=name_A, name_B=name_B)
        elif calc_type == "add":
            return "{name_A}+{name_B}".format(name_A=name_A, name_B=name_B)
        elif calc_type == "sub":
            return "{name_A}-{name_B}".format(name_A=name_A, name_B=name_B)


if __name__ == '__main__':
    app = QApplication([])
    md = MatrixCalcDialog()
    md.show()
    app.exec_()
