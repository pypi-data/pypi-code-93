import os

from PySide2.QtWidgets import QApplication, QLabel

from pmgwidgets import PMGPanel
from pyminer_comm import get_var_names
from utils import bind_panel_combo_ctrl_with_workspace

if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog


def format_dimension_name(dim_name: str, total_dims: int):
    """
    这个函数的作用是这样的：
    比如总维度为2的矩阵a ,维度0是行，维度1是列。
    总维度为3的array(三维张量)，维度0是空间高度坐标，维度1是行，维度2是列。
    Returns:

    """
    pass


class ReshapeTensorDialog(DFOperationDialog):
    def __init__(self, ):
        super(ReshapeTensorDialog, self).__init__()
        self.setWindowTitle("形状重整")
        self.combo_box.hide()
        self.hint_label.hide()
        names = get_var_names("array")
        if len(names) == 0:
            names = [self.no_var_in_workspace_hint()]
            name = self.no_var_in_workspace_hint()
        else:
            name = names[0]

        views = [
            ('combo_ctrl', 'variable', '要重整形状的变量', name, names),
            ("numberspin_ctrl", "dimension", self.tr("矩阵维度"), 2, "", (2, 10), 1),
        ]
        self.panel.set_items(views)
        self.panel.signal_settings_changed.connect(self.on_create_mode_changed)
        self.panel_input_dimension = PMGPanel()
        self.layout().addWidget(QLabel("输入矩阵各维度大小"))
        self.layout().addWidget(self.panel_input_dimension)
        self.layout().removeItem(self.button_layout)
        self.layout().addLayout(self.button_layout)

        self.panel_input_dimension.set_items([
            ("numberspin_ctrl", i, "维度%d" % i, 3, "", (1, 10000000), 1) for i in range(2)
        ])
        bind_panel_combo_ctrl_with_workspace(self.panel.get_ctrl('variable'))

        self.help_file_path = os.path.join(os.path.dirname(__file__), "helps", "reshape_tensor.md")

    def on_create_mode_changed(self, mode):
        """
        处理self.panel在创建矩阵模式变化的时候的事件
        Args:
            mode:

        Returns:

        """
        dimensions = mode["dimension"]

        self.panel_input_dimension.set_items([
            ("numberspin_ctrl", i, "维度%d" % i, 3, "", (1, 10000000), 1) for i in range(dimensions)
        ])

    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        dims = self.panel_input_dimension.get_value_with_filter()
        dim_list = [0] * len(dims.keys())
        for k, v in dims.items():
            dim_list[k] = v
        s = "("
        for dim_var in dim_list:
            s += str(dim_var) + ","
        s += ")"
        print(s)
        return "np.reshape({name},{arg_tup})".format(name=values['variable'], arg_tup=s)


if __name__ == '__main__':
    app = QApplication([])
    md = ReshapeTensorDialog()
    md.show()
    app.exec_()
