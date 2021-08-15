import logging
import os
from typing import TYPE_CHECKING, Callable

from PySide2.QtCore import QTranslator, QLocale
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QApplication
from pmgwidgets import PMGToolBar, create_icon
from features.extensions.extensionlib import BaseExtension, BaseInterface

from .stat_desc import StatDescForm

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from features.extensions.extensionlib import extension_lib

file_name = os.path.join(os.path.dirname(__file__), 'translations', 'qt_{0}.qm'.format(QLocale.system().name()))
app = QApplication.instance()
trans = QTranslator()
trans.load(file_name)
app.installTranslator(trans)


class PMStatsToolBar(PMGToolBar):
    drawing_item_double_clicked_signal: 'Signal' = Signal(str)
    extension_lib: 'extension_lib' = None
    variable = None

    def __init__(self):
        super().__init__()

        self.current_var_name = ''
        self.current_dataset_dtype = set()  # 保存当前数据集中存在的数据类型，确保不会重复

        self.add_tool_button('button_stat_desc', self.tr('Descriptive Statistics'), self.tr('Descriptive Statistics'),
                             create_icon(':/color/theme/default/icons/data_desc.svg'))
        self.add_tool_button('button_new_script', self.tr('Bayesian Statistics'), self.tr('Bayesian Statistics'),
                             create_icon(':/color/theme/default/icons/anova.svg'))
        self.addSeparator()
        self.add_tool_button('button_new_script', self.tr('Compare Means'), self.tr('Compare Means'),
                             create_icon(':/color/theme/default/icons/distribution.svg'))
        self.add_tool_button('button_new_script', self.tr('Missing Value Analysis'), self.tr('Missing Value Analysis'),
                             create_icon(':/color/theme/default/icons/data_join.svg'))
        self.addSeparator()
        self.add_tool_button('button_new_script', self.tr('General Linear Model'), self.tr('General Linear Model'),
                             create_icon(':/color/theme/default/icons/canshu.svg'))
        self.add_tool_button('button_new_script', self.tr('Generalized Linear Models'),
                             self.tr('Generalized Linear Models'),
                             create_icon(':/color/theme/default/icons/duoyuan.svg'))
        self.addSeparator()
        self.add_tool_button('button_new_script', self.tr('Correlate'), self.tr('Correlate'),
                             create_icon(':/color/theme/default/icons/jiashe.svg'))
        self.add_tool_button('button_new_script', self.tr('Regression'), self.tr('Regression'),
                             create_icon(':/color/theme/default/icons/regression.svg'))
        self.add_tool_button('button_new_script', self.tr('Classify'), self.tr('Classify'),
                             create_icon(':/color/theme/default/icons/Classification.svg'))
        self.addSeparator()

        self.add_tool_button('button_new_script', self.tr('Dimension Reduction'), self.tr('Dimension Reduction'),
                             create_icon(':/color/theme/default/icons/time_series.svg'))
        self.add_tool_button('button_new_script', self.tr('Survival'), self.tr('Survival'),
                             create_icon(':/color/theme/default/icons/shengcunfenxi.svg'))

        self.addSeparator()

    def get_toolbar_text(self) -> str:
        return self.tr('Stats')

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

    def bind_events(self):
        """
        绑定事件。这个将在界面加载完成之后被调用。
        """

        self.get_control_widget('button_stat_desc').clicked.connect(self.show_stat_desc)

    def show_stat_desc(self):
        self.stat_desc = StatDescForm()
        if len(self.current_var_name) > 0:
            self.stat_desc.current_dataset_name = self.current_var_name
            self.stat_desc.current_dataset = self.variable
            self.stat_desc.listWidget_var.addItems(list(self.variable.columns))
            self.stat_desc.current_dataset_columns = self.variable.columns
        else:
            self.stat_desc.setWindowTitle(self.stat_desc.windowTitle() + "--当前未选择变量")
        self.stat_desc.show()


class Extension(BaseExtension):
    if TYPE_CHECKING:
        interface: 'DrawingsInterface' = None
        widget: 'PMStatsToolBar' = None
        extension_lib: 'extension_lib' = None

    def on_loading(self):
        pass

    def on_load(self):
        statistics_toolbar: 'PMStatsToolBar' = self.widgets['PMStatsToolBar']
        statistics_toolbar.extension_lib = self.extension_lib
        self.statistics_toolbar = statistics_toolbar
        self.interface.drawing_item_double_clicked_signal = statistics_toolbar.drawing_item_double_clicked_signal

        self.interface.drawing_item_double_clicked_signal.connect(self.interface.on_clicked)
        self.interface.statistics_toolbar = statistics_toolbar

        self.extension_lib.Data.add_data_changed_callback(statistics_toolbar.on_data_modified)
        self.extension_lib.Signal.get_widgets_ready_signal().connect(self.bind_events)

    def bind_events(self):
        workspace_interface = self.extension_lib.get_interface('workspace_inspector')
        workspace_interface.add_select_data_callback(self.statistics_toolbar.on_data_selected)


class StatisticsInterface(BaseInterface):
    drawing_item_double_clicked_signal: 'Signal' = None
    drawings_toolbar: 'PMStatsToolBar' = None

    def on_clicked(self, name: str):
        pass

    def add_graph_button(self, name: str, text: str, icon_path: str, callback: Callable, hint: str = ''):
        """
        添加一个绘图按钮。name表示按钮的名称,text表示按钮的文字，icon_path表示按钮的图标路径，callback表示按钮的回调函数
        hint表示的就是按钮鼠标悬浮时候的提示文字。
        例如：
        extension_lib.get_interface('drawings_toolbar').add_graph_button('aaaaaa','hahahaahahah',
                                                                         ':/pyqt/source/images/lc_searchdialog.png',lambda :print('123123123'))
        """
        self.drawings_toolbar.add_toolbox_widget(name, text, icon_path, hint, refresh=True)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    sys.exit(app.exec_())
