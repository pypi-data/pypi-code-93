from kabaret.app.ui.gui.widgets.flow.flow_view import (
    CustomPageWidget,
    QtWidgets,
    QtCore,
    QtGui,
)
from fnmatch import fnmatch
from collections import defaultdict


class TaskFileItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, task_item, tree, file):
        super(TaskFileItem, self).__init__(task_item)
        self._tree = tree
        self._task_item = task_item
        self.file = None
        
        self.combo_box_revisions = QtWidgets.QComboBox()
        self._tree.setItemWidget(self, 1, self.combo_box_revisions)
        
        self.setCheckState(0, QtCore.Qt.Unchecked)
        self.setCheckState(2, QtCore.Qt.Unchecked)
        
        self.set_file(file)
    
    def set_file(self, file):
        self.file = file
        self._update()
    
    def on_checkstate_toggled(self, column):
        pass
    
    def submit_playblast_job(self):
        f = self.file
        kwargs = dict(
            shot_name=f['shot'],
            dept_name=f['department'],
            file_name=f['name'],
            revision_name=self.combo_box_revisions.currentText(),
        )
        extension = f['name'].split('.')[1]
        
        if extension == 'blend':
            kwargs['use_simplify'] = (self.checkState(2) == QtCore.Qt.Checked)
        
        return self._tree.parentWidget().submit_playblast_job(extension, **kwargs)
    
    def _update(self):
        f = self.file
        self.setText(0, f['name'])
        self.setText(2, '')
        
        names, statuses = zip(*f['revisions'])
        self.combo_box_revisions.addItems(names)
        self.combo_box_revisions.setCurrentText(f['default_revision'])
        
        for i, status in enumerate(statuses):
            if status != 'Available':
                self.combo_box_revisions.setItemData(i, False, QtGui.Qt.UserRole-1)


class ShotTaskItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, shot_item, tree, task):
        super(ShotTaskItem, self).__init__(shot_item)
        self._shot_item = shot_item
        self._tree = tree
        self.task = None
        
        self.setCheckState(0, QtCore.Qt.Unchecked)
        self.setCheckState(2, QtCore.Qt.Unchecked)
        
        self.set_task(task)
    
    def set_task(self, task):
        self.task = task
        self._update()
    
    def on_checkstate_toggled(self, column):
        for i in range(self.childCount()):
            self.child(i).setCheckState(column, self.checkState(column))
    
    def _update(self):
        d = self.task
        self.setText(0, d['name'])
        self.setText(2, '')
        
        # Loop over task files
        for file in d['files']:
            file_item = TaskFileItem(self, self._tree, file)


class ShotItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, shots_item, tree, shot):
        super(ShotItem, self).__init__(shots_item)
        self._tree = tree
        self.shot = None
        
        self.setCheckState(0, QtCore.Qt.Unchecked)
        self.setCheckState(2, QtCore.Qt.Unchecked)
        
        self.set_shot(shot)
    
    def set_shot(self, shot):
        self.shot = shot
        self._update()
    
    def on_checkstate_toggled(self, column):
        # Uncheck all tasks if shot is unchecked
        if self.checkState(column) == QtCore.Qt.Unchecked:
            for i in range(self.childCount()):
                self.child(i).setCheckState(column, QtCore.Qt.Unchecked)
            
            return
        
        # Otherwise, check tasks according to global tasks checkstates
        for i in range(self.childCount()):
            check_state = self._tree.get_task_item_checkstate(column, i)
            self.child(i).setCheckState(column, check_state)
    
    def _update(self):
        s = self.shot
        self.setText(0, s['name'])
        self.setText(2, '')
        
        for i in range(3):
            self.setBackgroundColor(i, QtGui.QColor(60, 60, 60))
        
        # Loop over shot tasks
        for task in s['tasks']:
            task_item = ShotTaskItem(self, self._tree, task)


class TaskItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, tasks_item, tree, task_name):
        super(TaskItem, self).__init__(tasks_item)
        self._tree = tree
        self.tasks_item = tasks_item
        
        self.setCheckState(0, QtCore.Qt.Unchecked)
        self.setCheckState(2, QtCore.Qt.Unchecked)
        
        self.setText(0, task_name)
        
        for i in range(3):
            self.setBackgroundColor(i, QtGui.QColor(60, 60, 60))
    
    def on_checkstate_toggled(self, column):
        index = self.tasks_item.indexOfChild(self)
        self._tree.set_task_items_checkstate(self.checkState(column), column, index)


class TasksItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, tree):
        super(TasksItem, self).__init__(tree)
        self._tree = tree
        
        self.setCheckState(0, QtCore.Qt.Unchecked)
        self.setCheckState(2, QtCore.Qt.Unchecked)
        
        self._update()
    
    def on_checkstate_toggled(self, column):
        for i in range(self.childCount()):
            self.child(i).setCheckState(column, self.checkState(column))
    
    def _update(self):
        self.setText(0, 'Tasks')
        
        for i in range(3):
            self.setBackgroundColor(i, QtGui.QColor(76, 80, 82))
            font = self.font(i)
            font.setWeight(QtGui.QFont.DemiBold)
            self.setFont(i, font)
        
        task_names = self._tree.parentWidget().get_shot_task_names()
        for task_name in task_names:
            task_item = TaskItem(self, self._tree, task_name)
        
        self.setExpanded(True)


class ShotsItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, tree):
        super(ShotsItem, self).__init__(tree)
        self._tree = tree
        
        self.setCheckState(0, QtCore.Qt.Unchecked)
        self.setCheckState(2, QtCore.Qt.Unchecked)
        
        self._update()
    
    def on_checkstate_toggled(self, column):
        for i in range(self.childCount()):
            self.child(i).setCheckState(column, self.checkState(column))
    
    def _update(self):
        self.setText(0, 'Shots')
        
        for i in range(3):
            self.setBackgroundColor(i, QtGui.QColor(76, 80, 82))
            font = self.font(i)
            font.setWeight(QtGui.QFont.DemiBold)
            self.setFont(i, font)
        
        shot_files_data = self._tree.parentWidget().get_shots_data()
        for shot in shot_files_data:
            shot_item = ShotItem(self, self._tree, shot)
        
        self.setExpanded(True)


class ShotSelector(QtWidgets.QTreeWidget):
    
    def __init__(self, parent, session):
        super(ShotSelector, self).__init__(parent)
        self.session = session

        columns = ('Name', 'Revision', 'Use simplify')
        self.setHeaderLabels(columns)
        self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.header().setStretchLastSection(False)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setFixedHeight(350)
        
        self.tasks = None
        self.shots = None
        self.refresh()
        
        # self.setMinimumHeight(self.sizeHintForRow(0) * (self.shots.childCount() + self.tasks.childCount()))
        
        self.itemChanged.connect(self.on_item_changed)
    
    def on_item_changed(self, item, column):
        item.on_checkstate_toggled(column)
    
    def set_task_items_checkstate(self, state, column, index):
        for i in range(self.shots.childCount()):
            shot_item = self.shots.child(i)
            
            if shot_item.checkState(0) == QtCore.Qt.Checked:
                task_item = shot_item.child(index)
                task_item.setCheckState(column, state)
    
    def get_task_item_checkstate(self, column, index):
        return self.tasks.child(index).checkState(column)
    
    def refresh(self):
        self.clear()
        
        self.tasks = TasksItem(self)
        self.shots = ShotsItem(self)


class ProcessSequenceFilesWidget(CustomPageWidget):

    def get_shots_data(self):
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name='ensure_files_data',
            args={}, kwargs={}
        )

    def _close_view(self):
        view = self.parentWidget().page.view
        view.close()


class RenderSequencePlayblastsWidget(ProcessSequenceFilesWidget):
    
    def build(self):
        self.shot_selector = ShotSelector(self, self.session)
        self.button_submit = QtWidgets.QPushButton('Submit playblasts')
        self.checkbox_select_all = QtWidgets.QCheckBox('Select all')
        self.combobox_pool = QtWidgets.QComboBox()
        self.lineedit_priority = QtWidgets.QLineEdit()
        
        self.button_submit.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.button_submit.setMaximumWidth(150)
        font = self.button_submit.font()
        font.setPointSize(11)
        font.setWeight(QtGui.QFont.DemiBold)
        self.button_submit.setFont(font)
        
        validator = QtGui.QIntValidator(1, 1000)
        self.lineedit_priority.setValidator(validator)
        self.lineedit_priority.setText('10')
        self.lineedit_priority.setFixedWidth(50)
        self.lineedit_priority.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        self.combobox_pool.addItems(self.get_job_pool_names())
        self.combobox_pool.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.combobox_pool.setFixedWidth(50)
        
        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self.shot_selector, 0, QtCore.Qt.AlignTop)
        
        vlo = QtWidgets.QVBoxLayout()
        label_settings = QtWidgets.QLabel('Global settings')
        label_settings.setFont(font)
        vlo.addWidget(label_settings, 0)
        vlo.addWidget(QtWidgets.QLabel('Priority'), 1)
        vlo.addWidget(self.lineedit_priority, 2)
        vlo.addWidget(QtWidgets.QLabel('Job pool'), 3)
        vlo.addWidget(self.combobox_pool, 4)
        vlo.addWidget(self.button_submit, 5)
        
        for i in range(5):
            vlo.setStretch(i, 0)
        vlo.insertStretch(5, 10)
        
        hlo.addLayout(vlo, 1)
        
        self.setLayout(hlo)

        self.button_submit.clicked.connect(self.on_submit_button_clicked)
    
    def get_job_pool_names(self):
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name='get_job_pool_names',
            args={}, kwargs={}
        )
    
    def get_shot_task_names(self):
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name='get_shot_task_names',
            args={}, kwargs={}
        )
    
    def submit_playblast_job(self, file_extension, **kwargs):
        kwargs['pool_name'] = self.combobox_pool.currentText()
        kwargs['priority'] = int(self.lineedit_priority.text())
        
        if file_extension == 'blend':
            method_name = 'submit_blender_playblast_job'
        elif file_extension == 'aep':
            method_name = 'submit_afterfx_playblast_job'
        else:
            pass
        
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name=method_name,
            args={}, kwargs=kwargs
        )
    
    def on_submit_button_clicked(self):
        shots = self.shot_selector.shots
        
        for i in range(shots.childCount()):
            shot_item = shots.child(i)
            
            for j in range(shot_item.childCount()):
                task_item = shot_item.child(j)
                
                for k in range(task_item.childCount()):
                    file_item = task_item.child(k)
                    
                    if file_item.checkState(0) == QtCore.Qt.Checked:
                        file_item.submit_playblast_job()
        
        self._close_view()
    
