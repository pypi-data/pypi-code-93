from PySide2.QtWidgets import QApplication, QMessageBox

from pyminer_comm import get_var_names
from utils import bind_panel_combo_ctrl_with_workspace

if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog


class MatrixInvDialog(DFOperationDialog):
    def __init__(self, ):
        super(MatrixInvDialog, self).__init__()
        self.setWindowTitle("矩阵求逆/转置")
        self.combo_box.hide()
        self.hint_label.hide()
        names = get_var_names()

        if len(names) == 0:
            names = [self.no_var_in_workspace_hint()]
            name_A = self.no_var_in_workspace_hint()
        else:
            name_A = names[0]
        views = [
            ('combo_ctrl', 'calc_type', self.tr('计算类型'), "inv",
             ["transpose", "inv", "pinv", "tensorinv"],
             ["转置", '逆矩阵', '矩阵伪逆', '张量逆']),
            ('combo_ctrl', 'mat', '矩阵 (numpy数组)', name_A, names),
        ]

        self.panel.set_items(views)
        bind_panel_combo_ctrl_with_workspace(self.panel.get_ctrl("mat"))

    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        name_A = values["mat"]
        calc_type = values["calc_type"]
        args_str = ''
        if calc_type == "inv":
            return "np.linalg.{func_name}({name_A})".format(func_name=calc_type, name_A=name_A)
        elif calc_type == "pinv":
            return "np.linalg.{func_name}({name_A})".format(func_name=calc_type, name_A=name_A)
        elif calc_type == "tensorinv":
            return "np.linalg.{func_name}({name_A})".format(func_name=calc_type, name_A=name_A)
        elif calc_type == "transpose":
            return "np.{func_name}({name_A})".format(func_name=calc_type, name_A=name_A)
        else:
            raise Exception(calc_type)


if __name__ == '__main__':
    app = QApplication([])
    md = MatrixInvDialog()
    md.show()
    app.exec_()
