import os

from PySide2.QtWidgets import QApplication, QMessageBox

from pyminer_comm import get_var_names
from utils import bind_panel_combo_ctrl_with_workspace

if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog


class NumericalIntegrationDialog(DFOperationDialog):
    def __init__(self, ):
        super(NumericalIntegrationDialog, self).__init__()
        self.setWindowTitle("数值积分")
        self.combo_box.hide()
        self.hint_label.hide()
        names = get_var_names()
        self.help_file_path = os.path.join(os.path.dirname(__file__), "helps", "numerical_integration.md")

        if len(names) == 0:
            names = [self.no_var_in_workspace_hint()]
            name = self.no_var_in_workspace_hint()
        else:
            name = names[0]
        views = [
            ('combo_ctrl', 'calc_type', self.tr('积分类型'), "quad",
             ["quad"],  # "dblquad"],
             ["一般定积分"]),  # '双重积分']),
            ('combo_ctrl', 'f', '被积函数', name, names),
            ('number_ctrl', 'a', '下限', 0, '',),
            ('number_ctrl', 'b', '上限', 1, '',),

        ]

        self.panel.set_items(views)
        bind_panel_combo_ctrl_with_workspace(self.panel.get_ctrl("f"))

    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        f = values.pop("f")
        calc_type = values.pop("calc_type")
        return "scipy.integrate.{func_name}({f},{args})".format(func_name=calc_type, f=f,
                                                                args=self.kwargs_to_str(values))


if __name__ == '__main__':
    app = QApplication([])
    md = NumericalIntegrationDialog()
    md.show()
    app.exec_()
