from PySide2.QtWidgets import QApplication

from pmgwidgets import FunctionGUIDialog

dic = {
    "title": "数据透视",
    "func_name": "pivot",
    "with_object": True,
    "args": [
        {
            "name": "index",
            "title": "行",
            "optional": True,
            "ctrl": {
                "type": "multitype_ctrl",
                "name": "index",
                "title": "选择行",
                "init": "",
                "types":
                    [{
                        "type_title": "字符串列表",
                        "ctrls": [
                            ("list_ctrl", "list_ctrl", '输入字符串列表',),
                        ],
                        "on_ok": lambda values: values["list_ctrl"][1]
                    }, {
                        "type_title": "字符串",
                        "ctrls": [
                            ("line_ctrl", "aaaa", '输入一个字符串', ""),
                        ],
                    }, {
                        "type_title": "选择变量",
                        "ctrls": [
                            ("vars_combo_ctrl", "variables", "选择变量", ""),
                        ],
                    }]
            }
        },
        {
            "name": "columns",
            "title": "选择列",
            "optional": False,
            "ctrl": ("multitype_ctrl", "columns", "选择列", "", [{
                "type_title": "字符串列表",
                "ctrls": [
                    ("list_ctrl", "list_ctrl", '输入字符串列表',),
                ],
                "on_ok": lambda values: values["list_ctrl"][1]
            }, {
                "type_title": "字符串",
                "ctrls": [
                    ("line_ctrl", "aaaa", '输入一个字符串', ""),
                ],
            }, {
                "type_title": "选择变量",
                "ctrls": [
                    ("vars_combo_ctrl", "variables", "选择变量", ""),
                ],
            }]),
        },

        {
            "name": "values",
            "title": "值",
            "optional": True,
            "ctrl": ("multitype_ctrl", 'values', "值", "", [{
                "type_title": "字符串列表",
                "ctrls": [
                    ("list_ctrl", "list_ctrl", '输入字符串列表', [[None, ], ['']], lambda: None),
                ],
                "on_ok": lambda values: values["list_ctrl"][1]
            }, {
                "type_title": "字符串",
                "ctrls": [
                    ("line_ctrl", "aaaa", '输入一个字符串', "Please input a string"),
                ],
            }, {
                "type_title": "选择变量",
                "ctrls": [
                    ("vars_combo_ctrl", "variables", "选择变量", ""),
                ],
            }])
        }
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
