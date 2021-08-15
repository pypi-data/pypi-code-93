from PySide2.QtWidgets import QApplication, QMessageBox

from pyminer_comm import get_var_names
from utils import bind_panel_combo_ctrl_with_workspace
if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog


class MatrixNumbersDialog(DFOperationDialog):
    def __init__(self, ):
        super(MatrixNumbersDialog, self).__init__()
        self.setWindowTitle("矩阵数值")
        self.combo_box.hide()
        self.hint_label.hide()
        names = get_var_names()

        if len(names) == 0:
            names = [self.no_var_in_workspace_hint()]
            name_A = self.no_var_in_workspace_hint()
        else:
            name_A = names[0]
        views = [
            ('combo_ctrl', 'calc_type', self.tr('计算类型'), "norm",
             ["norm", "cond", "det", "matrix_rank", "slogdet", "trace"],
             ["范数(当前仅支持2阶范数)", '条件数', '行列式', '秩', '行列式符号和自然对数', '对角线和']),
            ('combo_ctrl', 'mat', '矩阵 (numpy数组)', name_A, names),
        ]

        self.panel.set_items(views)
        bind_panel_combo_ctrl_with_workspace(self.panel.get_ctrl("mat"))

    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        name = values["mat"]
        calc_type = values["calc_type"]
        if calc_type in ["norm", "cond", "det", "matrix_rank", "slogdet"]:
            return "np.linalg.{func_name}({name})".format(func_name=calc_type, name=name)
        elif calc_type in ["trace"]:
            return "np.{func_name}({name})".format(func_name=calc_type, name=name)
        else:
            raise Exception(calc_type)


if __name__ == '__main__':
    app = QApplication([])
    md = MatrixNumbersDialog()
    md.show()
    app.exec_()
