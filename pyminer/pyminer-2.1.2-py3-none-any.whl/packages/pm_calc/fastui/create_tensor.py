import os

from PySide2.QtWidgets import QApplication, QLabel

from pmgwidgets import PMGPanel
from pyminer_comm import get_var_names

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
    if total_dims == 2:
        if dim_name.find("0") != -1:
            return "行数"
        elif dim_name.find("1") != -1:
            return '列数'
        else:
            raise ValueError((dim_name, total_dims))
    elif total_dims == 3:
        if dim_name.find("2") != -1:
            return "列数"
        elif dim_name.find("1") != -1:
            return "行数"
        elif dim_name.find("0") != -1:
            return "深度"
        else:
            raise ValueError((dim_name, total_dims))
    else:
        return dim_name


class CreateTensorDialog(DFOperationDialog):
    def __init__(self, ):
        super(CreateTensorDialog, self).__init__()
        self.setWindowTitle("矩阵/张量数组创建")
        self.combo_box.hide()
        self.hint_label.hide()
        names = get_var_names()

        views = [
            ('combo_ctrl', 'matrix_type', self.tr('数组类型'), "zeros",
             ["zeros", "ones", "full", "identity"],
             ['全0填充', '全1填充', "指定值填充所有元素", "单位矩阵（对角线1，其余0）"]),

            ('combo_ctrl', 'dtype', self.tr('数据类型'), "np.float64",
             ['np.int8', 'np.int16', 'np.int32', 'np.int64',
              'np.uint8', 'np.uint16', 'np.uint32', 'np.uint64',
              'np.float16', 'np.float32', 'np.float64', 'np.complex64', 'np.complex128'],
             ['8位 整数', '16位 整数', "32位 整数", "64位 整数",
              "8位 无符号整数", "16位 无符号整数", "32位 无符号整数", "64位 无符号整数",
              "16位 浮点数", "32位 浮点数", "64位 浮点数", "64位 复数", "128位 复数"]),

            ("numberspin_ctrl", "dimension", self.tr("数组维度"), 2, "", (2, 10), 1),
            ("number_ctrl", "fill_value", "填充值", -1, ""),
            ("numberspin_ctrl", "n", "n*n方阵长宽(n)", 3, "", (1, 10000), 1)
        ]

        self.panel.set_items(views)
        self.panel.signal_settings_changed.connect(self.on_create_mode_changed)
        self.panel_input_dimension = PMGPanel()
        self.panel.set_as_controller("matrix_type", ["fill_value"], "full")
        self.panel.set_as_controller("matrix_type", ["dimension"], lambda type: type != "identity", 'show')
        self.panel.set_as_controller("matrix_type", ["n"], lambda type: type != "identity", 'hide')
        self.label_before_panel = QLabel("输入各维度大小")
        self.layout().addWidget(self.label_before_panel)
        self.layout().addWidget(self.panel_input_dimension)
        self.layout().removeItem(self.button_layout)
        self.layout().addLayout(self.button_layout)

        self.panel_input_dimension.set_items([
            ("numberspin_ctrl", i, format_dimension_name("维度%d" % i, 2), 3, "", (1, 10000000), 1) for i in range(2)
        ])

        self.help_file_path = os.path.join(os.path.dirname(__file__), "helps", "reshape_tensor.md")

    def on_create_mode_changed(self, mode):
        """
        处理self.panel在创建矩阵模式变化的时候的事件
        Args:
            mode:

        Returns:

        """
        mat_type = mode["matrix_type"]
        print(mat_type)
        dimensions = mode["dimension"]
        print(dimensions)

        self.panel_input_dimension.set_items([
            ("numberspin_ctrl", i, format_dimension_name("维度%d" % i, dimensions), 3, "", (1, 10000000), 1) for i in
            range(dimensions)
        ])
        if mat_type in ["identity"]:
            self.label_before_panel.hide()
            self.panel_input_dimension.hide()
        else:
            self.label_before_panel.show()
            self.panel_input_dimension.show()

    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        func_name = values['matrix_type']
        dims = self.panel_input_dimension.get_value_with_filter()
        dim_list = [0] * len(dims.keys())

        for k, v in dims.items():
            dim_list[k] = v

        s = "("
        for dim_var in dim_list:
            s += str(dim_var) + ","
        s += ")"
        dtype = values.pop("dtype")
        if func_name in ["zeros", "ones"]:
            return "np.{func_name}({arg_tup}, {dtype})".format(func_name=func_name, arg_tup=s, dtype=dtype)
        elif func_name in ["full"]:
            fill_value = values["fill_value"]
            return "np.{func_name}({arg_tup},fill_value = {fill_value}, dtype={dtype})".format(func_name=func_name,
                                                                                               arg_tup=s,
                                                                                               fill_value=fill_value,
                                                                                               dtype=dtype)
        elif func_name in ["identity"]:
            n = values["n"]
            cmd = "np.{func_name}({n}, dtype={dtype})".format(func_name=func_name, n=n, dtype=dtype)
            return cmd


if __name__ == '__main__':
    app = QApplication([])
    md = CreateTensorDialog()
    md.show()
    app.exec_()
