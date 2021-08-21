from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QLabel
from qtpy.QtCore import QEvent, Qt
from magicgui import magicgui
from qtpy.QtCore import Signal, QObject, QEvent


class MyQLineEdit(QLineEdit):
    keyup = Signal()
    keydown = Signal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.keyup.emit()
            return
        elif event.key() == Qt.Key_Down:
            self.keydown.emit()
            return
        super().keyPressEvent(event)

class PluginSearch(QWidget):
    def __init__(self, napari_viewer):
        from napari.plugins import plugin_manager
        super().__init__()
        self.viewer = napari_viewer

        seach_field = MyQLineEdit("")
        results = QListWidget()

        def text_changed(*args, **kwargs):
            search_string = seach_field.text().lower()
            results.clear()
            for hook_type, (plugin_name, widgets) in plugin_manager.iter_widgets():
                for widget in widgets:
                    if search_string in plugin_name.lower() or search_string in widget.lower():
                        _add_result(results, plugin_name, widget)
            results.sortItems()

        def key_up():
            if results.currentRow() > 0:
                results.setCurrentRow(results.currentRow() - 1)

        def key_down():
            if results.currentRow() < results.count() - 1:
                results.setCurrentRow(results.currentRow() + 1)

        seach_field.keyup.connect(key_up)
        seach_field.keydown.connect(key_down)
        seach_field.textChanged.connect(text_changed)

        def item_double_clicked():
            item = results.currentItem()
            if item is not None:


                widget, widget_type = _get_widget(item.plugin_name, item.widget_name)

                if widget_type == "function":
                    napari_viewer.window.add_dock_widget(magicgui(widget), area='right', name=item.plugin_name + ": " + item.widget_name)
                else:
                    napari_viewer.window.add_plugin_dock_widget(item.plugin_name, item.widget_name)

                #    napari_viewer.window.add_dock_widget(widget(), area='right')

        seach_field.returnPressed.connect(item_double_clicked)
        results.itemDoubleClicked.connect(item_double_clicked)

        self.setLayout(QVBoxLayout())

        w = QWidget()
        w.setLayout(QHBoxLayout())
        w.layout().addWidget(QLabel("Search:"))
        w.layout().addWidget(seach_field)
        self.layout().addWidget(w)

        self.layout().addWidget(results)

def _add_result(results, plugin_name, widget_name):
    item = QListWidgetItem(plugin_name + ": " + widget_name)
    item.plugin_name = plugin_name
    item.widget_name = widget_name
    results.addItem(item)

def _get_widget(plugin_name, widget_name):
    from napari.plugins import plugin_manager
    if plugin_name in plugin_manager._function_widgets:
        functions = plugin_manager._function_widgets[plugin_name]
        if widget_name in functions:
            return functions[widget_name], "function"
    return plugin_manager.get_widget(plugin_name, widget_name)[0], "widget"

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return [PluginSearch]
