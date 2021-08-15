from PySide2.QtWidgets import QApplication

from pyminer_comm import get_var_names
from utils import bind_panel_combo_ctrl_with_workspace

if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog


class LinerEquationSolveDialog(DFOperationDialog):
    def __init__(self, ):
        super(LinerEquationSolveDialog, self).__init__()
        self.setWindowTitle("线性方程组求解")
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
            ('combo_ctrl', 'calc_type', self.tr('求解类型'), "solve",
             ["solve", "tensorsolve"],
             ['线性方程组AX=B', '张量方程AX=B']),
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
        if calc_type == "solve":
            pass
        elif calc_type == "tensorsolve":
            pass
        return "np.linalg.{func_name}({name_A},{name_B})".format(func_name=calc_type, name_A=name_A, name_B=name_B)


if __name__ == '__main__':
    app = QApplication([])
    md = LinerEquationSolveDialog()
    md.show()
    app.exec_()
