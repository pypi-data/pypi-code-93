import logging
import os
from typing import TYPE_CHECKING, Callable

from PySide2.QtCore import QTranslator, QLocale, Qt
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QApplication, QDialog

from features.extensions.extensionlib import BaseExtension, BaseInterface
from pmgwidgets import PMGToolBar, create_icon, Dict

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from features.extensions.extensionlib import extension_lib
from .fastui.matrix_calc import MatrixCalcDialog
from .fastui.matrix_inv import MatrixInvDialog
from .fastui.equation_solve import LinerEquationSolveDialog
from .fastui.matrix_numbers import MatrixNumbersDialog
from .fastui.numerical_integration import NumericalIntegrationDialog
from .fastui.create_tensor import CreateTensorDialog
from .fastui.create_vector import CreateVectorDialog
from .fastui.create_random_variable import CreateRandomVariablesDialog
from .fastui.reshape_tensor import ReshapeTensorDialog

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from features.extensions.extensionlib import extension_lib

file_name = os.path.join(os.path.dirname(__file__), 'translations', 'qt_{0}.qm'.format(QLocale.system().name()))
app = QApplication.instance()
trans = QTranslator()
trans.load(file_name)
app.installTranslator(trans)


class PMCalcToolBar(PMGToolBar):
    """
    矩阵计算：
      基本计算
      求逆与转置
      解线性方程组
      特征值或者其他数值(比如行列式、范数、特征值等)
      矩阵创建
    Sympy符号计算：
      1、
      2、
    """
    drawing_item_double_clicked_signal: 'Signal' = Signal(str)
    extension_lib: 'extension_lib' = None
    variable = None

    def __init__(self):
        super().__init__()
        self.op_windows: Dict[str, QDialog] = {}
        self.current_var_name = ''
        self.current_dataset_dtype = set()  # 保存当前数据集中存在的数据类型，确保不会重复
        resource_path = os.path.join(os.path.dirname(__file__), "icons")
        _j = os.path.join

        self.add_tool_button('button_create_tensor', self.tr('矩阵创建'), self.tr('创建矩阵或张量.要创建向量，请使用“向量创建”'),  # 矩阵创建
                             create_icon(_j(resource_path, "create.png")))

        self.add_tool_button('button_create_vector', self.tr('向量创建'), self.tr('创建向量。要创建矩阵或张量，请使用“矩阵创建”'),  # 矩阵创建
                             create_icon(_j(resource_path, "create.png")))

        self.add_tool_button('button_matrix_calc', self.tr('矩阵计算'),
                             self.tr('矩阵/向量计算，包含加、减、点乘、叉乘、转置'),  # 矩阵计算
                             create_icon(_j(resource_path, "matrix_calc.png")))

        self.add_tool_button('button_linear_equations', self.tr('线性方程组'), self.tr('线性方程组求解'),
                             create_icon(_j(resource_path, "equation_solve.png")))

        self.add_tool_button('button_matrix_inv', self.tr('求逆/转置'), self.tr('矩阵求逆与转置'),
                             create_icon(_j(resource_path, "flip.png")))

        self.add_tool_button('button_matrix_numbers', self.tr('矩阵数值'), self.tr('矩阵特征值、行列式、秩等'),
                             create_icon(_j(resource_path, "eigen.png")))

        self.add_tool_button('button_reshape_tensor', self.tr('形状重整'), self.tr('矩阵、张量的形状重整。\n比如将100*1的矩阵重整为10*10的方阵'),
                             create_icon(_j(resource_path, "reshape.png")))

        self.addSeparator()
        self.add_tool_button('button_create_random_variables', self.tr('创建随机变量'), self.tr('创建服从多种分布的一个或一组随机变量'),
                             create_icon(_j(resource_path, "rvs.png")))
        self.addSeparator()

        self.add_tool_button('button_numerical_integration', self.tr('数值积分'), self.tr('对函数进行积分'),
                             create_icon(_j(resource_path, "integrate.png")))

    def get_toolbar_text(self) -> str:
        return "计算"

    def on_data_selected(self, data_name: str):
        """
        当变量树中的数据被单击选中时，调用这个方法。
        """
        self.current_var_name = data_name
        logger.info('Variable clicked. Name is \'' + data_name)

    def on_data_modified(self, var_name: str, variable: object, data_source: str):
        """
        在数据被修改时，调用这个方法。
        """
        pass

    def on_close(self):
        self.hide()
        self.deleteLater()

    def show_window(self, window_name):
        window_dic = {
            "matrix_calc": MatrixCalcDialog,
            "matrix_inv": MatrixInvDialog,
            "linear_equations": LinerEquationSolveDialog,
            "matrix_numbers": MatrixNumbersDialog,
            "numerical_integration": NumericalIntegrationDialog,
            "create_tensor": CreateTensorDialog,
            "create_vector": CreateVectorDialog,
            "create_random_variables": CreateRandomVariablesDialog,
            "reshape_tensor":ReshapeTensorDialog
        }
        if window_name in self.op_windows.keys():
            self.op_windows[window_name].deleteLater()

        self.op_windows[window_name] = window_dic[window_name]()
        self.op_windows[window_name].setWindowFlags(
            self.op_windows[window_name].windowFlags() | Qt.WindowStaysOnTopHint)
        self.op_windows[window_name].show()

    def bind_events(self):
        """
        绑定事件。这个将在界面加载完成之后被调用。
        """
        self.get_control_widget('button_create_tensor').clicked.connect(lambda: self.show_window("create_tensor"))
        self.get_control_widget('button_create_vector').clicked.connect(lambda: self.show_window("create_vector"))

        self.get_control_widget('button_matrix_calc').clicked.connect(lambda: self.show_window("matrix_calc"))
        self.get_control_widget('button_linear_equations').clicked.connect(lambda: self.show_window("linear_equations"))
        self.get_control_widget('button_matrix_inv').clicked.connect(lambda: self.show_window("matrix_inv"))
        self.get_control_widget('button_matrix_numbers').clicked.connect(lambda: self.show_window("matrix_numbers"))



        self.get_control_widget('button_reshape_tensor').clicked.connect(lambda: self.show_window("reshape_tensor"))

        self.get_control_widget("button_create_random_variables").clicked.connect(
            lambda: self.show_window("create_random_variables"))

        self.get_control_widget('button_numerical_integration').clicked.connect(
            lambda: self.show_window("numerical_integration"))
        self.extension_lib.Signal.get_close_signal().connect(self.on_close)

    def slot_var_reload(self, str, dict):
        """
        刷新工作区间中的变量
        """
        import pandas as pd
        self.extension_lib.Data.set_var(str, pd.DataFrame.from_dict(dict))

    def insert_after(self) -> str:
        return "applications_toolbar"


class Extension(BaseExtension):
    if TYPE_CHECKING:
        interface: 'DrawingsInterface' = None
        widget: 'PMDrawingsToolBar' = None
        extension_lib: 'extension_lib' = None

    def on_loading(self):
        pass

    def on_load(self):
        drawings_toolbar: 'PMCalcToolBar' = self.widgets['PMCalcToolBar']
        drawings_toolbar.extension_lib = self.extension_lib
        self.drawings_toolbar = drawings_toolbar
        self.interface.drawing_item_double_clicked_signal = drawings_toolbar.drawing_item_double_clicked_signal

        self.interface.drawing_item_double_clicked_signal.connect(self.interface.on_clicked)
        self.interface.applications_toolbar = drawings_toolbar

        self.extension_lib.Data.add_data_changed_callback(drawings_toolbar.on_data_modified)
        self.extension_lib.Signal.get_widgets_ready_signal().connect(self.bind_events)

    def bind_events(self):
        workspace_interface = self.extension_lib.get_interface('workspace_inspector')
        workspace_interface.add_select_data_callback(self.drawings_toolbar.on_data_selected)


class CalcInterface(BaseInterface):
    drawing_item_double_clicked_signal: 'Signal' = None
    drawings_toolbar: 'PMDrawingsToolBar' = None

    def on_clicked(self, name: str):
        pass
        # print('interface', name)

    def add_graph_button(self, name: str, text: str, icon_path: str, callback: Callable, hint: str = ''):
        """
        添加一个绘图按钮。name表示按钮的名称,text表示按钮的文字，icon_path表示按钮的图标路径，callback表示按钮的回调函数
        hint表示的就是按钮鼠标悬浮时候的提示文字。
        例如：
        extension_lib.get_interface('drawings_toolbar').add_graph_button('aaaaaa','hahahaahahah',
                                                                         ':/pyqt/source/images/lc_searchdialog.png',lambda :print('123123123'))
        """
        self.drawings_toolbar.add_toolbox_widget(name, text, icon_path, hint, refresh=True)
