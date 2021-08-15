import ast
from typing import Any, List, Tuple

from PySide2.QtWidgets import QApplication

from pmgwidgets import FunctionGUIDialog


class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        super(CodeVisitor, self).__init__()
        self.preserved = {"pi", "e"}
        self.called = set()
        self.func_args = set()
        self._names = set()

    def visit_Name(self, node: ast.Name) -> Any:
        self._names.add(node.id)

    def visit_Call(self, node: ast.Call) -> Any:
        self.generic_visit(node)
        self.called.add(node.func.id)

    def get_result(self) -> Tuple[List[str], List[str]]:
        """

        Returns: 定义的名称，以及调用的ID名称。

        """
        names = self._names.copy()
        names.difference_update(self.preserved)
        names.difference_update(self.called)
        return list(names), list(self.called)


class Function():
    def __init__(self, s):
        self.name = s

    def __repr__(self):
        return self.name


def convert_to_lambda(code):
    print(code)
    original_code = code
    code = code.replace("np.", "")
    cv = CodeVisitor()
    cv.visit(ast.parse(code))
    args_list, funcs = cv.get_result()
    args = ''
    for a in args_list:
        args += a + ","
    args = args.strip(", ")

    ret = "lambda {ARGS}: {FCN}".format(ARGS=args, FCN=original_code)
    return Function(ret)


dic = {
    "title": "数据透视",
    "func_name": "scipy.integrate.dblquad",
    "with_object": False,
    "args": [
        {
            "name": "func",
            "title": "被积函数",
            "optional": False,
            "ctrl": {
                "type": "multitype_ctrl",
                "title": "选择被积函数",
                "init": "x*y",
                "types":
                    [{
                        "type_title": "输入表达式",
                        "ctrls": [
                            ("line_ctrl", "", '输入表达式并自动转换为函数', "np.sin(2*np.pi*x)"),
                        ],
                        "on_ok": lambda data: convert_to_lambda(data[""])
                    }, {
                        "type_title": "输入函数",
                        "ctrls": [
                            ("line_ctrl", "", '输入函数代码', "lambda x: np.sin(2*np.pi*x)"),
                        ],
                        "on_ok": lambda data: Function(data[""])
                    }, {
                        "type_title": "选择变量",
                        "ctrls": [
                            ("vars_combo_ctrl", "variable", "选择变量", ""),
                        ],
                    }]
            }
        },
        {
            "name": "hfun",
            "title": "内层函数上界",
            "optional": False,
            "ctrl": {
                "type": "multitype_ctrl",
                "title": "内层函数上界",
                "init": "np.sin(2*np.pi*x)",
                "types":
                    [{
                        "type_title": "输入表达式",
                        "ctrls": [
                            ("line_ctrl", "", '输入表达式并自动转换为函数', "np.sin(2*np.pi*x)"),
                        ],
                        "on_ok": lambda data: convert_to_lambda(data[""])
                    }, {
                        "type_title": "输入函数",
                        "ctrls": [
                            ("line_ctrl", "", '输入函数代码', "lambda x: np.sin(2*np.pi*x)"),
                        ],
                        "on_ok": lambda data: Function(data[""])
                    }, {
                        "type_title": "选择变量",
                        "ctrls": [
                            ("vars_combo_ctrl", "variable", "选择变量", ""),
                        ],
                    }]
            }
        },
        {
            "name": "gfun",
            "title": "内层函数下界",
            "optional": False,
            "ctrl": {
                "type": "multitype_ctrl",
                "title": "内层函数下界",
                "init": "lambda x:0",
                "types":
                    [{
                        "type_title": "输入表达式",
                        "ctrls": [
                            ("line_ctrl", "", '输入表达式并自动转换为函数', "np.sin(2*np.pi*x)"),
                        ],
                        "on_ok": lambda data: convert_to_lambda(data[""])
                    }, {
                        "type_title": "输入函数",
                        "ctrls": [
                            ("line_ctrl", "", '输入函数代码', "lambda x:0"),
                        ],
                        "on_ok": lambda data: Function(data[""])
                    }, {
                        "type_title": "选择变量",
                        "ctrls": [
                            ("vars_combo_ctrl", "variable", "选择变量", ""),
                        ],
                    }]
            }
        },
        {
            "name": "a",
            "title": "积分下限",
            "optional": False,
            "ctrl": {
                "type": "multitype_ctrl",
                "title": "积分下限",
                "init": 0,
                "types":
                    [{
                        "type_title": "输入下界",
                        "ctrls": [
                            ("number_ctrl", "", '输入下界', 0),
                        ],
                    }, {
                        "type_title": "选择变量",
                        "ctrls": [
                            ("vars_combo_ctrl", "variable", "选择变量", ""),
                        ],
                    }]
            }
        },
        {
            "name": "b",
            "title": "积分上限",
            "optional": False,
            "ctrl": {
                "type": "multitype_ctrl",
                "title": "积分上限",
                "init": 1,
                "types":
                    [{
                        "type_title": "输入数值",
                        "ctrls": [
                            ("number_ctrl", "", '输入数值', 1),
                        ]
                    }, {
                        "type_title": "选择变量",
                        "ctrls": [
                            ("vars_combo_ctrl", "variable", "选择变量", ""),
                        ],
                    }]
            }
        },
    ]

}


class PivotDialog(FunctionGUIDialog):
    def __init__(self):
        FunctionGUIDialog.__init__(self, dic)


if __name__ == '__main__':
    app = QApplication([])
    md = PivotDialog()
    md.show()
    app.exec_()
