import logging
import os
from typing import TYPE_CHECKING, Callable

from PySide2.QtCore import QTranslator, QLocale
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Signal

from pmgwidgets import PMGToolBar, create_icon
from features.extensions.extensionlib import BaseExtension, BaseInterface

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from features.extensions.extensionlib import extension_lib

file_name = os.path.join(os.path.dirname(__file__), 'translations', 'qt_{0}.qm'.format(QLocale.system().name()))
app = QApplication.instance()
trans = QTranslator()
trans.load(file_name)
app.installTranslator(trans)


class PMModellingToolBar(PMGToolBar):
    drawing_item_double_clicked_signal: 'Signal' = Signal(str)
    extension_lib: 'extension_lib' = None
    variable = None

    def __init__(self):
        super().__init__()
        self.add_tool_button('button_new_script', self.tr('Model Selection'), self.tr('Model Selection'),
                             create_icon(':/color/theme/default/icons/model_selection.svg'))

        self.add_tool_button('button_new_script', self.tr('Decision tree'), self.tr('Decision tree'),
                             create_icon(':/color/theme/default/icons/tree.svg'))
        self.add_tool_button('button_new_script', self.tr('ScoreCard'), self.tr('ScoreCard'),
                             create_icon(':/color/theme/default/icons/scorecard.svg'))
        self.addSeparator()
        self.add_tool_button('button_new_script', self.tr('Classify'), self.tr('Classify'),
                             create_icon(':/color/theme/default/icons/Classification.svg'))
        self.add_tool_button('button_new_script', self.tr('Regression'), self.tr('Regression'),
                             create_icon(':/color/theme/default/icons/regression.svg'))
        self.addSeparator()
        self.add_tool_button('button_new_script', self.tr('Clustering'), self.tr('Clustering'),
                             create_icon(':/color/theme/default/icons/Clustering.svg'))
        self.add_tool_button('button_new_script', self.tr('Dimension Reduction'), self.tr('Dimension Reduction'),
                             create_icon(':/color/theme/default/icons/reduce.svg'))

    def on_data_selected(self, data_name: str):
        """
        当变量树中的数据被单击选中时，调用这个方法。
        """
        logger.info('Variable clicked. Name is \'' + data_name)

    def on_data_modified(self, var_name: str, variable: object, data_source: str):
        """
        在数据被修改时，调用这个方法。
        """
        pass

    def on_close(self):
        self.hide()
        self.deleteLater()

    def refresh_pos(self):
        """
        刷新顶上的ToplevelWidget的位置。
        """
        return
        btn = self.get_control_widget('button_show_more_plots')
        panel: 'pmgwidgets.TopLevelWidget' = self.get_control_widget(
            'drawing_selection_panel')
        width = self.get_control_widget('button_list').width()
        panel.set_width(width)
        panel.set_position(QPoint(btn.x() - width, btn.y()))

    def get_toolbar_text(self) -> str:
        return self.tr('Modelling')


class Extension(BaseExtension):
    if TYPE_CHECKING:
        interface: 'ModellingInterface' = None
        widget: 'PMDrawingsToolBar' = None
        extension_lib: 'extension_lib' = None

    def on_loading(self):
        pass

    def on_load(self):
        drawings_toolbar: 'PMModellingToolBar' = self.widgets['PMModellingToolBar']
        drawings_toolbar.extension_lib = self.extension_lib
        self.drawings_toolbar = drawings_toolbar
        self.interface.drawing_item_double_clicked_signal = drawings_toolbar.drawing_item_double_clicked_signal

        self.interface.drawing_item_double_clicked_signal.connect(self.interface.on_clicked)
        self.interface.drawings_toolbar = drawings_toolbar

        self.extension_lib.Data.add_data_changed_callback(drawings_toolbar.on_data_modified)
        self.extension_lib.Signal.get_widgets_ready_signal().connect(self.bind_events)

    def bind_events(self):
        workspace_interface = self.extension_lib.get_interface('workspace_inspector')
        workspace_interface.add_select_data_callback(self.drawings_toolbar.on_data_selected)


class ModellingInterface(BaseInterface):
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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    sys.exit(app.exec_())
