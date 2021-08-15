from PySide2.QtWidgets import QApplication

from pmgwidgets import PMGPanel
from pyminer_comm import get_var_names

if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog

dtype_combo = ('combo_ctrl', 'dtype', '数据类型', "np.float64",
               ['np.int8', 'np.int16', 'np.int32', 'np.int64',
                'np.uint8', 'np.uint16', 'np.uint32', 'np.uint64',
                'np.float16', 'np.float32', 'np.float64', 'np.complex64', 'np.complex128'],
               ['8位 整数', '16位 整数', "32位 整数", "64位 整数",
                "8位 无符号整数", "16位 无符号整数", "32位 无符号整数", "64位 无符号整数",
                "16位 浮点数", "32位 浮点数", "64位 浮点数", "64位 复数", "128位 复数"]),


class CreateVectorDialog(DFOperationDialog):
    def __init__(self, ):
        super(CreateVectorDialog, self).__init__()
        self.setWindowTitle("创建向量")
        self.combo_box.hide()
        self.hint_label.hide()
        names = get_var_names()

        views = [
            ('combo_ctrl', 'vector_type', self.tr('矩阵类型'), "arange",
             ["arange", "linspace", "logspace"],
             ['一定步长、线性变化(arange)', '一定数量、线性变化(linspace)', "一定数量、对数变化(logspace)"]),
            dtype_combo,  # 插入一个数据类型的判断框
            ('number_ctrl', 'start', '起始', 0, "", None),
            ('number_ctrl', 'stop', '停止', 1, "", None),
            ('number_ctrl', 'step', '步长', 0.1, "", None),
            ('numberspin_ctrl', 'num', '数量', 10, "", (0, 1000_000_000)),
            ('number_ctrl', 'base', '底数(自然对数为字母e)', 2, "", None),
            # ('combo_ctrl', 'B', 'B', name_B, names)
        ]

        self.panel.set_items(views)
        self.panel.set_as_controller("vector_type", ["base"], "logspace", "show")  # 按规则隐藏。
        self.panel.set_as_controller("vector_type", ["step"], "arange", "show")
        self.panel.set_as_controller("vector_type", ["num"],
                                     lambda vector_type: vector_type in ["linspace", "logspace"], "show")
        self.panel_input_dimension = PMGPanel()
        self.layout().addWidget(self.panel_input_dimension)

    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        vector_type = values.pop("vector_type")
        dtype = values.pop("dtype")
        return "np.{func_name}({kwargs_str}, dtype={dtype})".format(func_name=vector_type,
                                                                   kwargs_str=self.kwargs_to_str(values).rstrip(", "), dtype=dtype)


if __name__ == '__main__':
    app = QApplication([])
    md = CreateVectorDialog()
    md.show()
    app.exec_()
