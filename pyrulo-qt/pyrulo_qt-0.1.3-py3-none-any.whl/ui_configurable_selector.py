from PySide2 import QtWidgets, QtCore
from propsettings_qt.ui_settings_area import SettingsAreaWidget
from pyrulo import class_imports


class ConfigurableSelector(QtWidgets.QWidget):
	"""
	Widget para cargar clases que hereden de una clase base especificada
	e inicializar un combobox con instancias de dichas clases. Consta de dos elementos agrupados en un vertical layout.
	El primero es el combobox. El segundo es un area para configurar las uiproperties del objeto seleccionado.
	"""
	eventObjectSelected = QtCore.Signal(object)

	def __init__(self, dir_key, parent=None):
		super(ConfigurableSelector, self).__init__(parent)
		self._dir_key = dir_key
		self._objects = []
		self._current_index = 0

		layout = QtWidgets.QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(layout)

		self._combobox = QtWidgets.QComboBox(self)
		self._combobox.currentIndexChanged.connect(self._selection_changed)
		self._combobox.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
		self.layout().addWidget(self._combobox)

		self._conf_properties = SettingsAreaWidget()
		self._conf_properties.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
		self.layout().addWidget(self._conf_properties)

		self._populate_objects()

	def populate_class(self, dir_key):
		"""
		Inicializar el combobox con una nueva clase.
		:param class_dir:
		:param clazz:
		:return:
		"""
		self._dir_key = dir_key
		self._populate_objects()

	def _populate_objects(self):
		"""
		Inicializar el combobox.
		:return:
		"""
		classes = class_imports.import_classes_by_key(self._dir_key)
		classes = sorted(classes, key=lambda cls: str(cls))
		for cls in classes:
			instance = cls()
			self._objects.append(instance)
			self._combobox.addItem(str(instance))
		self.eventObjectSelected.emit(self.current_object())

	def _selection_changed(self, index):
		self._current_index = index
		current_object = self.current_object()
		self._conf_properties.populate_configurations(current_object)
		self.eventObjectSelected.emit(current_object)

	def current_object(self):
		if len(self._objects) > 0:
			return self._objects[self._current_index]
		else:
			return None
