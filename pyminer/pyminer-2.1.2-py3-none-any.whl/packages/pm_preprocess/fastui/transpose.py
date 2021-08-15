from PySide2.QtWidgets import QApplication

if not __name__ == '__main__':
    from .base import DFOperationDialog
else:
    from base import DFOperationDialog


class TransposeDialog(DFOperationDialog):
    def __init__(self, ):
        super(TransposeDialog, self).__init__()
        self.setWindowTitle("转置")
        views = [
            # ('check_ctrl', 'copy', self.tr('Copy'), False),
            # ('check_ctrl', 'inplace', self.tr('In Place'), False),  # 直接覆盖之前的变量。注意，并没有这个参数。
        ]
        self.panel.set_items(views)


    def get_value_code(self) -> str:
        values = self.panel.get_value_with_filter()  # 只获取使能并且可见的控件的值
        varname = self.combo_box.currentText()
        args_str = ''
        for k, v in values.items():
            args_str += '{k}={v},'.format(k=k, v=repr(v))
        code = '{varname}.transpose({args})'.format(varname=varname, args=args_str)
        return code


if __name__ == '__main__':
    app = QApplication([])
    md = TransposeDialog()
    md.show()
    app.exec_()
