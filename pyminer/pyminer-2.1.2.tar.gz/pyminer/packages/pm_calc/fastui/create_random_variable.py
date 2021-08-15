"""
rvs:
    norm: loc = 0,scale=1,size=1。 loc相当于常见的μ，scale相当于常见的σ。
    gamma: a, loc=0, scale=1,size=1。a就是α, scale是1/β。建议输入的是alpha和beta。
    weibull_min分布: c, loc=0, scale=1,size=1 。c是β，scale是η，loc是γ。
    chi2: df,loc=0,scale=1,size=1。 df代表的就是自由度，一般也记作n。
    expon: loc=0,scale=1,size=1 scale为1/λ。
"""
import os

from PySide2.QtWidgets import QApplication

from pmgwidgets import PMGPanel
from pyminer_comm import get_var_names

if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog

controls = {"norm":
    {"params": [
        {"name": "mu", "title": "μ（中心值）", "range": (float("-inf"), float("inf")), "type": "number_ctrl", "init": 0},
        {"name": "sigma", "title": "σ（标准差）", "range": (0, float("inf")), "type": "number_ctrl", "init": 1},
    ], "fmt_func": {
        "sigma": lambda sigma: f"scale={sigma}",
        "mu": lambda mu: f"loc={mu}"
    }  # 将返回结果转换为函数。
    }, "gamma":
    {"params": [
        {"name": "alpha", "title": "α", "range": (float("-inf"), float("inf")), "type": "number_ctrl", "init": 1},
        {"name": "beta", "title": "β", "range": (float("-inf"), float("inf")), "type": "number_ctrl", "init": 1},
        {"name": "loc", "title": "位置参数", "range": (float("-inf"), float("inf")), "type": "number_ctrl", "init": 0}
    ], "fmt_func": {
        "alpha": lambda alpha: f"a={alpha}",
        "beta": lambda beta: f"scale=1/{beta}"
    }
    }, "weibull_min":  # c, loc=0, scale=1。c是β，scale是η，loc是γ。
    {"params": [
        {"name": "beta", "title": "β（形状参数,常也作k）", "range": (float("-inf"), float("inf")), "type": "number_ctrl",
         "init": 1},
        {"name": "eta", "title": "η（尺度参数,常也作λ）", "range": (float("-inf"), float("inf")), "type": "number_ctrl",
         "init": 1},
        {"name": "gamma", "title": "γ（位置参数,常也作t0）", "range": (float("-inf"), float("inf")), "type": "number_ctrl",
         "init": 0}
    ], "fmt_func": {
        "eta": lambda eta: f"scale={eta}",
        "gamma": lambda gamma: f"loc={gamma}",
        "beta": lambda beta: f"c={beta}"
    }
    }, "chi2":  # df,loc=0,scale=1,size=1。 df代表的就是自由度，一般也记作n。
    {"params": [
        {"name": "df", "title": "n （自由度）", "range": (float("-inf"), float("inf")), "type": "number_ctrl", "init": 1},
        {"name": "scale", "title": "尺度参数", "range": (float("-inf"), float("inf")), "type": "number_ctrl", "init": 1},
        {"name": "loc", "title": "t0（位置参数）", "range": (float("-inf"), float("inf")), "type": "number_ctrl", "init": 0}
    ], "fmt_func": {}
    }, "expon":
    {"params": [  # expon: loc=0,scale=1,size=1 scale为1/λ。
        {"name": "lamda", "title": "λ（形状参数）", "range": (float("-inf"), float("inf")), "type": "number_ctrl", "init": 1},
        {"name": "loc", "title": "t0（位置参数）", "range": (float("-inf"), float("inf")), "type": "number_ctrl", "init": 0}
    ], "fmt_func": {
        "lamda": lambda lamda: f"scale=1/{lamda}"
    }
    }
}


class CreateRandomVariablesDialog(DFOperationDialog):
    def __init__(self, ):
        super(CreateRandomVariablesDialog, self).__init__()
        self.setWindowTitle("创建随机变量")
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
            ('combo_ctrl', 'dist_type', self.tr('分布类型'), "norm",
             ["norm", "gamma", "weibull_min", "chi2", "expon"],  # "dblquad"],
             ["正态分布", "Γ分布", "威布尔分布", "卡方分布", "指数分布"]),  # '双重积分']),
            ('numberspin_ctrl', 'size', '变量个数', 1, '', (0, 2 ** 30)),
        ]

        self.panel.set_items(views)

        self.panel_params_input = PMGPanel()

        self.layout().removeItem(self.button_layout)
        self.layout().addWidget(self.panel_params_input)
        self.layout().addLayout(self.button_layout)

        views2 = []
        print(controls["norm"]["params"])
        self.panel_params_input.set_items(controls["norm"]["params"])
        self.panel.set_param_changed_callback("dist_type", self.on_dist_type_changed)

        self.panel.set_value({"dist_type": "weibull_min"})
        # bind_panel_combo_ctrl_with_workspace(self.panel.get_ctrl("f"))

    def on_dist_type_changed(self, val):
        """
        当分布种类发生变化的时候，调用这个方法
        Args:
            val:

        Returns:

        """
        dist_type = val["dist_type"]
        self.panel_params_input.set_items(controls[dist_type]["params"])

    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        params = self.panel_params_input.get_value_with_filter()
        dist_type = values.pop("dist_type")

        args_str = ""
        for param_name, param_value in params.items():
            fmt_func = controls[dist_type]["fmt_func"].get(param_name)
            if fmt_func is not None:
                args_str += fmt_func(param_value) + ","
            else:
                args_str += f"{param_name}={param_value},"
        args_str += self.kwargs_to_str({"size": values["size"]})

        cmd = "scipy.stats.{dist_type}.rvs({args_str})".format(dist_type=dist_type, args_str=args_str)
        print(cmd)
        return cmd


if __name__ == '__main__':
    app = QApplication([])
    md = CreateRandomVariablesDialog()
    md.show()
    app.exec_()
