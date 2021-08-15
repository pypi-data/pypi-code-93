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

from .datareplace import DataReplaceForm
from .datamissingvalue import DataMissingValueForm
from .data_filter import DataFilterForm
from .fastui import MergeDialog
from .fastui.pivot import PivotDialog

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from features.extensions.extensionlib import extension_lib

if TYPE_CHECKING:
    from .fastui import TransposeDialog, FillNADialog, DropNADialog
else:
    from .fastui import TransposeDialog, FillNADialog, DropNADialog

file_name = os.path.join(os.path.dirname(__file__), 'translations', 'qt_{0}.qm'.format(QLocale.system().name()))
app = QApplication.instance()
trans = QTranslator()
trans.load(file_name)
app.installTranslator(trans)


class PMPreprocessToolBar(PMGToolBar):
    drawing_item_double_clicked_signal: 'Signal' = Signal(str)
    extension_lib: 'extension_lib' = None
    variable = None

    def __init__(self):
        super().__init__()
        self.op_windows: Dict[str, QDialog] = {}
        self.current_var_name = ''
        self.current_dataset_dtype = set()  # 保存当前数据集中存在的数据类型，确保不会重复
        self.add_tool_button('button_data_filter', self.tr('Filter'), self.tr('Filter'),
                             create_icon(':/color/theme/default/icons/filter.svg'))
        self.add_tool_button('button_data_replace', self.tr('Find/Replace'), self.tr('Find/Replace'),
                             create_icon(':/color/theme/default/icons/replace.svg'))
        self.add_tool_button('button_data_info', self.tr('Data Info'), self.tr('Data Info'),
                             create_icon(':/color/theme/default/icons/data_info.svg'))

        self.add_tool_button('button_pivot', self.tr('数据透视'), self.tr('选择行列并制作数据透视表'),
                             create_icon(':/color/theme/default/icons/data_info.svg'))

        self.add_tool_button('button_data_column', self.tr('Column'), self.tr('Column'),
                             create_icon(':/color/theme/default/icons/column.svg'))
        self.addSeparator()
        self.add_tool_button('button_data_role', self.tr('Data Role'), self.tr('Data Role'),
                             create_icon(':/color/theme/default/icons/data_role.svg'))
        self.add_tool_button('button_data_partition', self.tr('Data Partition'), self.tr('Data Partition'),
                             create_icon(':/color/theme/default/icons/data_partition.svg'))
        self.addSeparator()
        self.add_tool_button('button_data_add_row', self.tr('New Row'), self.tr('New Row'),
                             create_icon(':/color/theme/default/icons/add_row.svg'))
        self.add_tool_button('button_data_add_column', self.tr('New Column'), self.tr('New Column'),
                             create_icon(':/color/theme/default/icons/add_col.svg'))
        self.add_tool_button('button_data_delete_row', self.tr('Delete Row'), self.tr('Delete Row'),
                             create_icon(':/color/theme/default/icons/delete_row.svg'))
        self.add_tool_button('button_data_delete_column', self.tr('Delete Column'), self.tr('Delete Column'),
                             create_icon(':/color/theme/default/icons/delete_col.svg'))
        self.addSeparator()
        self.add_tool_button('button_data_dropna', self.tr('Drop Missing Value'), self.tr('Missing Value'),
                             create_icon(':/color/theme/default/icons/missing_value.svg'))
        self.add_tool_button('button_data_fillna', self.tr('Fill Missing Value'), self.tr('Missing Value'),
                             create_icon(':/color/theme/default/icons/missing_value.svg'))
        self.add_tool_button('button_data_sample', self.tr('Sample'), self.tr('Sample'),
                             create_icon(':/color/theme/default/icons/sample.svg'))
        self.add_tool_button('button_data_transposition', self.tr('Transpose'), self.tr('Transpose'),
                             create_icon(':/color/theme/default/icons/transposition.svg'))
        self.addSeparator()
        self.add_tool_button('button_data_merge_v', self.tr('Vertical Merger'), self.tr('Vertical Merger'),
                             create_icon(':/color/theme/default/icons/merge_v.svg'))
        self.add_tool_button('button_data_merge_h', self.tr('Horizontal Merger'), self.tr('Horizontal Merger'),
                             create_icon(':/color/theme/default/icons/merge_h.svg'))
        self.addSeparator()
        self.add_tool_button('button_data_join', self.tr('Join'), self.tr('Join'),
                             create_icon(':/color/theme/default/icons/data_join.svg'))
        self.add_tool_button('button_data_scale', self.tr('Normalization'), self.tr('Normalization'),
                             create_icon(':/color/theme/default/icons/scale.svg'))

        self.addSeparator()

    def get_toolbar_text(self) -> str:
        return self.tr('Preprocess')

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
            'transpose': TransposeDialog,
            'fillna': FillNADialog,
            'dropna': DropNADialog,
            "pivot": PivotDialog,
        }
        if window_name not in self.op_windows.keys():
            self.op_windows[window_name] = window_dic[window_name]()
            self.op_windows[window_name].setWindowFlags(
                self.op_windows[window_name].windowFlags() | Qt.WindowStaysOnTopHint)
        self.op_windows[window_name].show()

    def bind_events(self):
        """
        绑定事件。这个将在界面加载完成之后被调用。
        """
        self.get_control_widget('button_data_filter').clicked.connect(self.show_data_filter)
        self.get_control_widget('button_pivot').clicked.connect(lambda: self.show_window("pivot"))

        self.get_control_widget('button_data_replace').setEnabled(False)  # clicked.connect(self.show_data_replace)

        self.get_control_widget('button_data_fillna').clicked.connect(lambda: self.show_window('fillna'))
        self.get_control_widget('button_data_dropna').clicked.connect(lambda: self.show_window('dropna'))

        self.get_control_widget('button_data_info').setEnabled(False)  # .clicked.connect(self.show_data_info)
        self.get_control_widget('button_data_column').setEnabled(False)  # .clicked.connect(self.show_data_column)
        self.get_control_widget('button_data_role').setEnabled(False)  # .clicked.connect(self.show_data_role)
        self.get_control_widget('button_data_partition').setEnabled(False)  # .clicked.connect(self.show_data_partition)
        self.get_control_widget('button_data_add_row').setEnabled(False)  # .clicked.connect(self.show_data_add_row)
        self.get_control_widget('button_data_add_column').setEnabled(
            False)  # .clicked.connect(self.show_data_add_column)
        self.get_control_widget('button_data_delete_row').setEnabled(
            False)  # .clicked.connect(self.show_data_delete_row)
        self.get_control_widget('button_data_delete_column').setEnabled(
            False)  # .clicked.connect(self.show_data_delete_column)
        self.get_control_widget('button_data_partition').setEnabled(False)  # .clicked.connect(self.show_data_info)
        self.get_control_widget('button_data_sample').setEnabled(False)  # .clicked.connect(self.show_data_info)
        self.get_control_widget('button_data_transposition').clicked.connect(lambda: self.show_window('transpose'))
        self.get_control_widget('button_data_merge_v').clicked.connect(lambda: self.show_data_merger(0))
        self.get_control_widget('button_data_merge_h').clicked.connect(lambda: self.show_data_merger(1))
        # self.get_control_widget('button_data_partition').clicked.connect(self.show_data_info)
        self.get_control_widget('button_data_join').setEnabled(False)  # .clicked.connect(self.show_data_info)
        self.get_control_widget('button_data_scale').setEnabled(False)  # clicked.connect(self.show_data_scale)

        self.extension_lib.Signal.get_close_signal().connect(self.on_close)

    def show_data_merger(self, axis: int):
        dlg = MergeDialog(axis)
        dlg.exec_()

    def show_data_missing(self):
        self.data_missing = DataMissingValueForm()
        self.data_missing.show()

    def show_data_scale(self):
        self.data_scale = DataFilterForm()
        self.data_scale.show()

    def show_data_filter(self):
        """
        显示 "数据筛选" 窗口
        """
        self.data_filter = DataFilterForm()
        if len(self.current_var_name) > 0:
            self.data_filter.current_dataset = self.variable
            self.data_filter.current_dataset_name = self.current_var_name
            self.data_filter.comboBox_columns.addItems(list(self.variable.columns))
            for col in self.variable.columns:
                self.current_dataset_dtype.add(str(self.variable.loc[:, col].dtype))
            self.data_filter.comboBox_dtype.addItems(list(self.current_dataset_dtype))
            self.data_filter.dataset_init()
        else:
            self.data_filter.setWindowTitle(self.data_filter.windowTitle() + '--未选择数据')

        self.data_filter.signal_data_change.connect(self.slot_var_reload)  # 信号处理

        self.data_filter.show()

    def slot_var_reload(self, str, dict):
        """
        刷新工作区间中的变量
        """
        import pandas as pd
        self.extension_lib.Data.set_var(str, pd.DataFrame.from_dict(dict))

    def show_data_replace(self):
        self.data_replace = DataReplaceForm()
        self.data_replace.show()


class Extension(BaseExtension):
    if TYPE_CHECKING:
        interface: 'DrawingsInterface' = None
        widget: 'PMDrawingsToolBar' = None
        extension_lib: 'extension_lib' = None

    def on_loading(self):
        pass

    def on_load(self):
        drawings_toolbar: 'PMPreprocessToolBar' = self.widgets['PMPreprocessToolBar']
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


class PreprocessInterface(BaseInterface):
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
