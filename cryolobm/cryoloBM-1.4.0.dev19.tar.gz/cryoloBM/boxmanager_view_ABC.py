try:
    QT = 4
    import PyQt4.QtGui as QtG
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QFontMetrics,QFont
    import matplotlib.backends.backend_qt4agg as plt_qtbackend
except ImportError:
    QT = 5
    import PyQt5.QtWidgets as QtG
    from PyQt5.QtGui import QFontMetrics,QFont
    import PyQt5.QtCore as QtCore
    import matplotlib.backends.backend_qt5agg as plt_qtbackend

from abc import abstractmethod
import cryoloBM.__init__ as ini
from cryoloBM import constants,helper_GUI,boxmanager_toolbar
from typing import Tuple,List
from numpy import ndarray
import matplotlib.pyplot as plt

class Boxmanager_view_ABC(QtG.QMainWindow):
    def __init__(self, font:QFont)->None:
        self.font = font
        super(Boxmanager_view_ABC, self).__init__(None)
        self.current_image_path = None
        self.image_folder_path = None

        # when we change the combobox layout the 'currentIndexChanged' is triggered. We have to avoid to run the function
        self.is_updating_cb = False

        # it is used for disabled pop up messages when update params and GUI
        self.is_updating_params = False

        # figure and axes var
        self.fig, self.ax = None,None

        # self.fig.canvas
        self.background_current = None
        self.background_current_onmove = None       # for managing the real time filament picking

        # plot var
        self.plot = None

        # var to show the image (it ll be self.ax.imshow)
        self.im = None

        # flag for identifying if a slider is pressed
        self.is_slider_pressed = False

        self.show_confidence_histogram_action = QtG.QAction("Confidence histogram", self)
        self.show_size_distribution_action = QtG.QAction("Size distribution", self)

        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu("&File")
        self.plotMenu = self.mainMenu.addMenu("&Plot")

        self.layout = None
        self.tree = QtG.QTreeWidget(self)
        self.current_tree_item = None

        self.zoom_update = False

        self.preview_win = None     # The preview window
        self.preview_is_on = False # True when the preview win (i.e.: tracing results) is displayed

        # Init params and related Qt object used in the tabs
        # VISUALIZATION TAB
        self.boxsize_line = QtG.QLineEdit(str(constants.Default_settings_value.DEFAULT_BOX_SIZE.value))
        self.button_set_box_size = QtG.QPushButton("Set")
        self.boxsize_label = QtG.QLabel("Box size: ")

        self.visualization_label = QtG.QLabel("Visualization: ")

        self.visualization_combobox = QtG.QComboBox()

        # the box distance is visible only when we are picking filaments. i.e.. Picking combobox set on FILAMENT
        self.box_distance_filament_line = QtG.QLineEdit(str(constants.Default_settings_value.DEFAULT_BOX_DISTANCE_FILAMENT_SIZE.value))
        self.button_set_box_distance_filament = QtG.QPushButton("Set")
        self.box_distance_filament_label = QtG.QLabel("Box distance: ")
        self.button_set_box_distance_filament.setVisible(False)
        self.box_distance_filament_label.setVisible(False)
        self.box_distance_filament_line.setVisible(False)

        self.use_estimated_size_label = QtG.QLabel("Use estimated size:")
        self.use_estimated_size_checkbox = QtG.QCheckBox()

        self.picking_label = QtG.QLabel("Picking:")
        self.picking_filament_combox = QtG.QComboBox()

        # THRESHOLDING TAB
        self.lower_size_thresh_label = QtG.QLabel("Minimum size: ")
        self.lower_size_thresh = constants.Default_settings_value.DEFAULT_LOWER_SIZE_THRESH.value
        self.lower_size_thresh_slide = QtG.QSlider(QtCore.Qt.Horizontal)
        self.lower_size_thresh_line = QtG.QLineEdit(
            str(constants.Default_settings_value.DEFAULT_LOWER_SIZE_THRESH.value))

        self.upper_size_thresh_label = QtG.QLabel("Maximum size: ")
        self.upper_size_thresh = constants.Default_settings_value.DEFAULT_UPPER_SIZE_THRESH.value
        self.upper_size_thresh_slide = QtG.QSlider(QtCore.Qt.Horizontal)
        self.upper_size_thresh_line = QtG.QLineEdit(
            str(constants.Default_settings_value.DEFAULT_UPPER_SIZE_THRESH.value))

        self.current_conf_thresh = constants.Default_settings_value.DEFAULT_CURRENT_CONF_THRESH.value
        self.conf_thresh_label = QtG.QLabel("Confidence threshold: ")
        self.conf_thresh_slide = QtG.QSlider(QtCore.Qt.Horizontal)
        self.conf_thresh_line = QtG.QLineEdit(str(constants.Default_settings_value.DEFAULT_CURRENT_CONF_THRESH.value))

        self.current_num_boxes_thresh = constants.Default_settings_value.DEFAULT_CURRENT_NUM_BOXES_THRESH.value
        self.num_boxes_thres_label = QtG.QLabel("Number boxes threshold: ")
        self.num_boxes_thresh_slide = QtG.QSlider(QtCore.Qt.Horizontal)
        self.num_boxes_thresh_line = QtG.QLineEdit(
            str(constants.Default_settings_value.DEFAULT_CURRENT_NUM_BOXES_THRESH.value))

        # FILTERING TAB
        self.filter_freq = constants.Default_settings_value.DEFAULT_FILTER_FREQ.value
        self.filter_line = QtG.QLineEdit(str(self.filter_freq))
        self.low_pass_filter_label = QtG.QLabel("Low pass filter cut-off: ")
        self.button_apply_filter = QtG.QPushButton("Apply")
        self.janny_label = QtG.QLabel("Janny denoising: ")
        self.button_janny = QtG.QPushButton("Run")

        # TRACING TAB
        self.preview_label = QtG.QLabel("Preview")
        self.preview_checkbox = QtG.QCheckBox()
        self.button_trace = QtG.QPushButton("Trace")

        self.search_range = constants.Default_settings_value.DEFAULT_SEARCH_RANGE.value
        self.search_range_line = QtG.QLineEdit(str(self.search_range))
        self.search_range_label = QtG.QLabel("Search range: ")
        self.search_range_slider = QtG.QSlider(QtCore.Qt.Horizontal)

        self.memory = constants.Default_settings_value.DEFAULT_MEMORY.value
        self.memory_line = QtG.QLineEdit(str(self.memory))
        self.memory_label = QtG.QLabel("Memory: ")
        self.memory_slider = QtG.QSlider(QtCore.Qt.Horizontal)

        self.min_length = constants.Default_settings_value.DEFAULT_MIN_LENGTH.value
        self.min_length_line = QtG.QLineEdit(str(self.min_length))
        self.min_length_label = QtG.QLabel("Minimum length: ")
        self.min_length_slider = QtG.QSlider(QtCore.Qt.Horizontal)

        # param for tracking the filament
        self.win_size = None  # it will set for default to 'self.box_size'
        self.win_size_line = QtG.QLineEdit()
        self.win_size_label = QtG.QLabel("Window size: ")
        self.win_size_slider = QtG.QSlider(QtCore.Qt.Horizontal)

        self.min_edge_weight = constants.Default_settings_value.DEFAULT_MIN_EDGE_WEIGHT.value
        self.min_edge_weight_line = QtG.QLineEdit(str(self.min_edge_weight))
        self.min_edge_weight_label = QtG.QLabel("Minimum edge weight: ")
        self.min_edge_weight_slider = QtG.QSlider(QtCore.Qt.Horizontal)

        # add tabs
        self.tabs = QtG.QTabWidget()
        self.tab_visualization = QtG.QWidget()
        self.tab_thresholding = QtG.QWidget()
        self.tab_tracing = QtG.QWidget()
        self.tab_tracing.setToolTip("THE TRACING IS AVAILABLE ONLY FOR TOMO ")
        self.tab_filtering = QtG.QWidget()

    def setup_(self)->None:
        # SETUP QT
        self.setWindowTitle("BoxManager " + ini.__version__)
        central_widget = QtG.QWidget(self)

        self.setCentralWidget(central_widget)

        # Center on screen
        resolution = QtG.QDesktopWidget().screenGeometry()
        self.move(
            (resolution.width() / 2) - (self.frameSize().width() / 2),
            (resolution.height() / 2) - (self.frameSize().height() / 2),
            )

        # Setup Menu
        close_action = QtG.QAction("Close", self)
        close_action.setShortcut("Ctrl+Q")
        close_action.setStatusTip("Leave the app")
        close_action.triggered.connect(self.close_boxmanager)

        open_image_folder = QtG.QAction("Folder", self)
        open_image_folder.triggered.connect(self.open_SPA_folder)     # it was open_image_folder

        open_image = QtG.QAction("File", self)
        open_image.triggered.connect(self.open_SPA_image)

        open_image_3D_folder = QtG.QAction("Folder", self)
        open_image_3D_folder.triggered.connect(self.open_tomo_folder) #it was open_image3D_folder

        open_image3D_tomo = QtG.QAction("File", self)
        open_image3D_tomo.triggered.connect(self.open_tomo_image)       # it was open_image3D_tomo

        import_box_folder = QtG.QAction("Import box files", self)
        import_box_folder.triggered.connect(self.import_box_files)        # ii was load_box_files

        save_data = QtG.QAction("Save", self)
        save_data.triggered.connect(self.save_on_files)  #it was write_all_type

        resetMenu = QtG.QAction("Reset", self)
        resetMenu.triggered.connect(self.reset_config)

        self.show_confidence_histogram_action.triggered.connect( self.show_confidence_histogram)
        self.show_confidence_histogram_action.setEnabled(False)

        self.show_size_distribution_action.triggered.connect(self.show_size_distribution)
        self.show_size_distribution_action.setEnabled(False)

        openMenu = self.fileMenu.addMenu("&Open")
        openMenuSPA = openMenu.addMenu("&SPA")
        openMenuSPA.addAction(open_image_folder)
        openMenuSPA.addAction(open_image)
        openMenuTomo = openMenu.addMenu("&Tomogram")
        openMenuTomo.addAction(open_image_3D_folder)
        openMenuTomo.addAction(open_image3D_tomo)

        self.fileMenu.addAction(import_box_folder)
        self.fileMenu.addAction(save_data)
        self.fileMenu.addAction(resetMenu)

        self.fileMenu.addAction(close_action)

        self.plotMenu.addAction(self.show_confidence_histogram_action)
        self.plotMenu.addAction(self.show_size_distribution_action)

        # Setup tree
        self.setMenuBar(self.mainMenu)

        self.layout = QtG.QGridLayout(central_widget)

        self.tree.setHeaderHidden(True)
        self.layout.addWidget(self.tree, 0, 0, 1, 3)
        self.tree.currentItemChanged.connect(self.event_image_changed)
        self.tree.itemChanged.connect(helper_GUI.event_checkbox_changed)

        self.tabs.addTab(self.tab_visualization, "Visualization")
        self.tabs.addTab(self.tab_thresholding, "Thresholding")
        self.tabs.addTab(self.tab_filtering, "Filtering")

        self.create_tab_visualization()
        self.create_tab_filtering()
        self.create_tab_thresholding()
        self.create_tab_tracing()

        #add tabs to widget
        line_counter = 1
        # picking_filament
        self.picking_label.setEnabled(True)
        self.layout.addWidget(self.picking_label, line_counter, 0)
        line_counter = line_counter + 1
        self.picking_filament_combox.addItems([constants.Picking_cb.PARTICLE.value,constants.Picking_cb.FILAMENT.value])
        self.picking_filament_combox.setEnabled(True)
        self.picking_filament_combox.currentIndexChanged.connect(self.picking_filament_changed)
        self.layout.addWidget(self.picking_filament_combox, line_counter, 0)
        line_counter = line_counter + 1

        self.layout.addWidget(self.tabs, line_counter, 0)

        # Show image selection
        self.show()

    @abstractmethod
    def create_tab_filtering(self)->None:
        line_counter = 1
        layout = QtG.QGridLayout()

        #todo: uncomment these lines when the janny option will be implemented
        """
        It is still not implemented and we make it invisibl 
        #run janny
        self.janny_label.setEnabled(True)
        layout.addWidget(self.janny_label, line_counter, 0)
        self.button_janny.clicked.connect(self.janny)
        layout.addWidget(self.button_janny, line_counter, 1)
        line_counter += 1
        """

        # Low pass filter setup
        self.low_pass_filter_label.setEnabled(True)
        layout.addWidget(self.low_pass_filter_label, line_counter, 0)
        layout.addWidget(self.filter_line, line_counter, 1)
        self.filter_line.returnPressed.connect(self.apply_filter)
        self.button_apply_filter.clicked.connect(self.apply_filter)
        self.button_apply_filter.setEnabled(False)
        layout.addWidget(self.button_apply_filter, line_counter, 2)

        self.tab_filtering.setLayout(layout)

    @abstractmethod
    def create_tab_visualization(self)->None:
        line_counter = 1
        layout = QtG.QGridLayout()

        # Box size setup
        layout.addWidget(self.boxsize_label, line_counter, 0)
        self.boxsize_line.returnPressed.connect(self.box_size_changed)
        layout.addWidget(self.boxsize_line, line_counter, 1)
        self.button_set_box_size.clicked.connect(self.box_size_changed)
        layout.addWidget(self.button_set_box_size, line_counter, 2)
        line_counter = line_counter + 1

        # Use circle instead of rectangle
        self.visualization_label.setEnabled(True)
        layout.addWidget(self.visualization_label, line_counter, 0)
        self.visualization_combobox.addItems([constants.Visualization_cb.RECT.value, constants.Visualization_cb.CIRCLE.value])
        self.visualization_combobox.currentIndexChanged.connect(self.visualization_changed)
        self.visualization_combobox.setEnabled(True)
        layout.addWidget(self.visualization_combobox, line_counter, 1)
        line_counter = line_counter + 1

        # box picking distance
        layout.addWidget(self.box_distance_filament_label, line_counter, 0)
        self.box_distance_filament_line.returnPressed.connect(self.box_distance_filament_changed)
        layout.addWidget(self.box_distance_filament_line, line_counter, 1)
        self.button_set_box_distance_filament.clicked.connect(self.box_distance_filament_changed)
        layout.addWidget(self.button_set_box_distance_filament, line_counter, 2)
        #self.is_box_distance_filament_visible(is_visible=False)

        line_counter = line_counter + 1

        # Show estimated size
        self.use_estimated_size_label.setEnabled(False)
        layout.addWidget(self.use_estimated_size_label, line_counter, 0)
        layout.addWidget(self.use_estimated_size_checkbox, line_counter, 1)
        self.use_estimated_size_checkbox.stateChanged.connect(self.use_estimated_size_changed)
        self.use_estimated_size_checkbox.setEnabled(False)
        self.tab_visualization.setLayout(layout)

    @abstractmethod
    def create_tab_thresholding(self)->None:
        line_counter = 1
        layout = QtG.QGridLayout()

        # Lower size
        layout.addWidget(self.lower_size_thresh_label, line_counter, 0)
        self.lower_size_thresh_slide.setMinimum(constants.Default_settings_value.DEFAULT_LOWER_SIZE_THRESH.value)
        self.lower_size_thresh_slide.setMaximum(500)
        self.lower_size_thresh_slide.setValue(constants.Default_settings_value.DEFAULT_LOWER_SIZE_THRESH.value)
        self.lower_size_thresh_slide.valueChanged.connect(self.lower_size_thresh_changed)
        self.lower_size_thresh_slide.sliderPressed.connect(self.slider_pressed)
        self.lower_size_thresh_slide.sliderReleased.connect(lambda: self.changed_slider_release( type_call= constants.Slider_release_fcall.LOWER_SIZE.value))
        self.lower_size_thresh_slide.setTickPosition(QtG.QSlider.TicksBelow)
        self.lower_size_thresh_slide.setTickInterval(1)
        layout.addWidget(self.lower_size_thresh_slide, line_counter, 1)

        self.lower_size_thresh_line.textChanged.connect(self.lower_size_label_changed)
        layout.addWidget(self.lower_size_thresh_line, line_counter, 2)
        self.lower_size_thresh_line.returnPressed.connect(self.lower_size_label_changed)

        line_counter = line_counter + 1

        # Upper size threshold
        layout.addWidget(self.upper_size_thresh_label, line_counter, 0)
        self.upper_size_thresh_slide.setMinimum(0)
        self.upper_size_thresh_slide.setMaximum(constants.Default_settings_value.DEFAULT_UPPER_SIZE_THRESH.value)
        self.upper_size_thresh_slide.setValue(constants.Default_settings_value.DEFAULT_UPPER_SIZE_THRESH.value)
        self.upper_size_thresh_slide.valueChanged.connect(self.upper_size_thresh_changed)
        self.upper_size_thresh_slide.sliderPressed.connect(self.slider_pressed)
        self.upper_size_thresh_slide.sliderReleased.connect(lambda: self.changed_slider_release( type_call= constants.Slider_release_fcall.UPPER_SIZE.value))
        self.upper_size_thresh_slide.setTickPosition(QtG.QSlider.TicksBelow)
        self.upper_size_thresh_slide.setTickInterval(1)
        layout.addWidget(self.upper_size_thresh_slide, line_counter, 1)
        self.upper_size_thresh_line.textChanged.connect(self.upper_size_label_changed)
        layout.addWidget(self.upper_size_thresh_line, line_counter, 2)
        self.upper_size_thresh_line.returnPressed.connect(self.upper_size_label_changed)

        line_counter = line_counter + 1

        # Confidence threshold setup
        layout.addWidget(self.conf_thresh_label, line_counter, 0)
        self.conf_thresh_slide.setMinimum(0)
        self.conf_thresh_slide.setMaximum(100)
        self.conf_thresh_slide.setValue(30)
        self.conf_thresh_slide.valueChanged.connect(self.conf_thresh_changed)
        self.conf_thresh_slide.sliderPressed.connect(self.slider_pressed)
        self.conf_thresh_slide.sliderReleased.connect(lambda: self.changed_slider_release( type_call= constants.Slider_release_fcall.CONF.value))
        self.conf_thresh_slide.setTickPosition(QtG.QSlider.TicksBelow)
        self.conf_thresh_slide.setTickInterval(1)
        layout.addWidget(self.conf_thresh_slide, line_counter, 1)
        self.conf_thresh_line.textChanged.connect(self.conf_thresh_label_changed)
        layout.addWidget(self.conf_thresh_line, line_counter, 2)
        self.conf_thresh_line.returnPressed.connect(self.conf_thresh_label_changed)

        line_counter = line_counter + 1

        # number of boxes threshold setup
        layout.addWidget(self.num_boxes_thres_label, line_counter, 0)
        self.num_boxes_thresh_slide.setMinimum(constants.Default_settings_value.DEFAULT_MIN_NUM_BOXES_THRESH.value)
        self.num_boxes_thresh_slide.setMaximum(constants.Default_settings_value.DEFAULT_MAX_NUM_BOXES_THRESH.value)
        self.num_boxes_thresh_slide.setValue(constants.Default_settings_value.DEFAULT_CURRENT_NUM_BOXES_THRESH.value)
        #self.num_boxes_thresh_slide.valueChanged.connect(self.num_boxes_thresh_changed)
        #self.num_boxes_thresh_slide.sliderPressed.connect(self.slider_pressed)
        #self.num_boxes_thresh_slide.sliderReleased.connect(self.changed_slider_release_num_boxes_thresh)
        self.num_boxes_thresh_slide.setTickPosition(QtG.QSlider.TicksBelow)
        self.num_boxes_thresh_slide.setTickInterval(1)
        layout.addWidget(self.num_boxes_thresh_slide, line_counter, 1)
        #self.num_boxes_thresh_line.textChanged.connect(self.num_boxes_thresh_label_changed)
        layout.addWidget(self.num_boxes_thresh_line, line_counter, 2)
        # self.num_boxes_thresh_line.returnPressed.connect(self.num_boxes_thresh_label_changed)

        #helper_GUI.thresholding_tab_blurring(controller, is_enable=False, kind_of_cbox=False, has_filament=False)
        self.tab_thresholding.setLayout(layout)

    @abstractmethod
    def create_tab_tracing(self)->None:
        """
        this tab is not created at the run of the GUI but it will appear automatically after loading cbox untraced file
        """

        # when it ll be usable we ll let blurred some options in not filament case
        self.tabs.addTab(self.tab_tracing, "Tracing")
        line_counter = 1
        layout = QtG.QGridLayout()

        #run tracing_searchRange
        layout.addWidget(self.search_range_label, line_counter, 0)
        self.search_range_slider.setMinimum(0)
        self.search_range_slider.setMaximum(1000)   # it ll be change in real time when we change tomo
        self.search_range_slider.setValue(constants.Default_settings_value.DEFAULT_SEARCH_RANGE.value)
        self.search_range_slider.valueChanged.connect(self.searchRange_changed)
        self.search_range_slider.sliderPressed.connect(self.slider_pressed)
        self.search_range_slider.sliderReleased.connect(lambda: self.changed_slider_release( type_call= constants.Slider_release_fcall.SEARCH_RANGE.value))
        self.search_range_slider.setTickPosition(QtG.QSlider.TicksBelow)
        self.search_range_slider.setTickInterval(1)
        layout.addWidget(self.search_range_slider, line_counter, 1)
        self.search_range_line.textChanged.connect(self.searchRange_label_changed)
        self.search_range_line.returnPressed.connect(self.searchRange_label_changed)
        layout.addWidget(self.search_range_line, line_counter, 2)
        line_counter += 1

        #run tracing_memory
        layout.addWidget(self.memory_label, line_counter, 0)
        self.memory_slider.setMinimum(0)
        self.memory_slider.setMaximum(1000)     # it ll be change in real time when we change tomo
        self.memory_slider.setValue(constants.Default_settings_value.DEFAULT_MEMORY.value)
        self.memory_slider.valueChanged.connect(self.memory_changed)
        self.memory_slider.sliderPressed.connect(self.slider_pressed)
        self.memory_slider.sliderReleased.connect(lambda: self.changed_slider_release( type_call= constants.Slider_release_fcall.MEMORY.value))
        self.memory_slider.setTickPosition(QtG.QSlider.TicksBelow)
        self.memory_slider.setTickInterval(1)
        layout.addWidget(self.memory_slider, line_counter, 1)
        self.memory_line.textChanged.connect(self.memory_label_changed)
        self.memory_line.textChanged.connect(self.memory_label_changed)
        layout.addWidget(self.memory_line, line_counter, 2)
        line_counter += 1

        #run tracing_min_length
        layout.addWidget(self.min_length_label, line_counter, 0)
        self.min_length_slider.setMinimum(0)
        self.min_length_slider.setMaximum(1000)    # it ll be change in real time when we change tomo
        self.min_length_slider.setValue(constants.Default_settings_value.DEFAULT_MIN_LENGTH.value)
        self.min_length_slider.valueChanged.connect(self.min_length_changed)
        self.min_length_slider.sliderPressed.connect(self.slider_pressed)
        self.min_length_slider.sliderReleased.connect(lambda: self.changed_slider_release( type_call= constants.Slider_release_fcall.MIN_LENGTH.value))
        self.min_length_slider.setTickPosition(QtG.QSlider.TicksBelow)
        self.min_length_slider.setTickInterval(1)
        layout.addWidget(self.min_length_slider, line_counter, 1)
        self.min_length_line.textChanged.connect(self.min_length_label_changed)
        self.min_length_line.textChanged.connect(self.min_length_label_changed)
        layout.addWidget(self.min_length_line, line_counter, 2)
        line_counter += 1

        # usable only in filament case
        layout.addWidget(self.min_edge_weight_label, line_counter, 0)
        self.min_edge_weight_slider.setMinimum(0)
        self.min_edge_weight_slider.setMaximum(100)
        self.min_edge_weight_slider.setValue(constants.Default_settings_value.DEFAULT_MIN_EDGE_WEIGHT.value * 100)
        self.min_edge_weight_slider.valueChanged.connect(self.min_edge_weight_changed)
        self.min_edge_weight_slider.sliderPressed.connect(self.slider_pressed)
        self.min_edge_weight_slider.sliderReleased.connect(lambda: self.changed_slider_release(type_call= constants.Slider_release_fcall.MIN_EDGE_W.value))
        self.min_edge_weight_slider.setTickPosition(QtG.QSlider.TicksBelow)
        self.min_edge_weight_slider.setTickInterval(1)
        layout.addWidget(self.min_edge_weight_slider, line_counter, 1)
        self.min_edge_weight_line.textChanged.connect(self.min_edge_weight_label_changed)
        self.min_edge_weight_line.textChanged.connect(self.min_edge_weight_label_changed)
        layout.addWidget(self.min_edge_weight_line, line_counter, 2)
        line_counter += 1

        self.win_size = constants.Default_settings_value.DEFAULT_BOX_SIZE.value
        layout.addWidget(self.win_size_label, line_counter, 0)
        self.win_size_line.setText(str(self.win_size))
        self.win_size_slider.setMinimum(0)
        self.win_size_slider.setValue(self.win_size)
        self.min_edge_weight_slider.valueChanged.connect(self.win_size_changed)
        self.min_edge_weight_slider.sliderPressed.connect(self.slider_pressed)
        self.win_size_slider.sliderReleased.connect(lambda: self.changed_slider_release(type_call= constants.Slider_release_fcall.WIN_SIZE.value))
        self.win_size_slider.setTickPosition(QtG.QSlider.TicksBelow)
        self.win_size_slider.setTickInterval(1)
        layout.addWidget(self.win_size_slider, line_counter, 1)
        self.win_size_line.textChanged.connect(self.win_size_label_changed)
        self.win_size_line.textChanged.connect(self.win_size_label_changed)
        layout.addWidget(self.win_size_line, line_counter, 2)
        line_counter += 1

        # run the 3D preview
        layout.addWidget(self.preview_label, line_counter, 0)
        self.preview_checkbox.stateChanged.connect(self.preview)
        layout.addWidget(self.preview_checkbox, line_counter, 1)

        # run the 3D trace
        self.button_trace.clicked.connect(self.trace)
        layout.addWidget(self.button_trace, line_counter, 2)
        self.tracing_tab_blurring(is_enable=False, has_filament=False)
        self.tab_tracing.setLayout(layout)

    @abstractmethod
    def reset_config(self) -> None:
        """
        reset function called after clicking Reset->File
        It is defined in the controller, it calls self.reset_config_ and controller.model.reset_config
        """
        pass

    def reset_config_(self)->None:
        """
        Reset config function called by the controller
        """
        # no reset 'current_image_path', otherwise after resetting we cannot change image
        #self.current_image_path = None
        # reset tab Visualization
        self.boxsize_line.setText(str(constants.Default_settings_value.DEFAULT_BOX_SIZE.value))
        self.box_distance_filament_line.setText(str(constants.Default_settings_value.DEFAULT_BOX_DISTANCE_FILAMENT_SIZE.value))
        self.use_estimated_size_checkbox.setEnabled(False)
        self.use_estimated_size_label.setEnabled(False)

        self.set_picking_combobox(is_enabled=True)
        self.set_visibility_box_distance(is_visible=False)
        self.set_visualization_combobox(is_picking_particles=True)

        # it is disabled after importing TRACED filament
        self.button_set_box_size.setEnabled(True)
        self.boxsize_line.setEnabled(True)
        self.boxsize_label.setEnabled(True)

        # reset tab Tracing
        self.preview_is_on = False
        self.preview_win = None

        self.is_updating_cb = False
        self.is_slider_pressed = False

        self.is_updating_params = True
        self.use_estimated_size_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.preview_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.is_updating_params = False

        self.zoom_update = False

        # i restore the clean canvas in case of file->reset
        self.background_current_onmove = self.fig.canvas.copy_from_bbox(self.ax.bbox) if self.fig else None
        self.background_current = self.fig.canvas.copy_from_bbox(self.ax.bbox) if self.fig else None


    @abstractmethod
    def set_picking_combobox(self,  is_enabled: bool) -> None:
        """
        It fills the picking combobox of the main window
        :param is_enabled: False it is blurred
        """
        helper_GUI.set_picking_combobox(self,is_enabled=is_enabled)

    @abstractmethod
    def set_visualization_combobox(self, is_picking_particles: bool) -> None:
        """
        It fills the 'visualization' combobox of the 'visualization' tab in function of the picking combobox value
        :param is_picking_particles: True if the picking combobox is set to 'Particles'
        """
        self.is_updating_cb = True
        helper_GUI.set_visualization_combobox(self,is_picking_particles=is_picking_particles)
        self.is_updating_cb = False

    @abstractmethod
    def set_visibility_box_distance(self, is_visible: bool) -> None:
        """
        It makes the 'box distance' buttons and line of the 'visualization' tab visible or not
        :param is_visible: True makes visible these widgets
        """
        helper_GUI.set_visibility_box_distance(self,is_visible=is_visible)

    @abstractmethod
    def reset_tree(self, root:QtG, title:str)->None:
        self.current_tree_item = None
        self.tree.clear()
        self.tree.setColumnCount(2)
        self.tree.setHeaderHidden(False)
        self.tree.setHeaderLabels(["Filename", "Number of boxes"])
        if self.plot is not None:
            self.plot.close()
        self.tree.addTopLevelItem(root)
        fm = QFontMetrics(self.font)
        w = fm.width(title)
        self.tree.setMinimumWidth(w + 150)
        self.tree.setColumnWidth(0, 300)

    @abstractmethod
    def slider_pressed(self)->None:
        self.is_slider_pressed = True
        self.is_updating_params = True

    @abstractmethod
    def changed_slider_release(self,  type_call:constants.Slider_release_fcall)->None:
        """
        Is triggered by releasing a slider
        :param type_call: identify which slider was released
        """
        self.is_slider_pressed = False
        self.is_updating_params = False
        if type_call == constants.Slider_release_fcall.CONF.value:
            self.conf_thresh_changed()
        elif type_call == constants.Slider_release_fcall.LOWER_SIZE.value:
            self.lower_size_thresh_changed()
        elif type_call == constants.Slider_release_fcall.UPPER_SIZE.value:
            self.upper_size_thresh_changed()
        elif type_call == constants.Slider_release_fcall.MEMORY.value:
            self.memory_changed()
        elif type_call == constants.Slider_release_fcall.MIN_EDGE_W.value:
            self.min_edge_weight_changed()
        elif type_call == constants.Slider_release_fcall.MIN_LENGTH.value:
            self.min_length_changed()
        elif type_call == constants.Slider_release_fcall.SEARCH_RANGE.value:
            self.searchRange_changed()
        elif type_call == constants.Slider_release_fcall.WIN_SIZE.value:
            self.win_size_changed()


        self.is_updating_params = False
        # we do not want live tracing for filament case
        # real time visualization and thresholding will be managed directly in their function
        #helper_tab_tracing.check_and_run_preview(controller=controller,only_reload=True)

    def set_first_time_img(self,im:ndarray)->None:
        """
        Set the variable to show an image
        :param im: np array
        :return: none
        """
        # Create figure and axes
        self.fig, self.ax = plt.subplots(1)

        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)

        self.fig.tight_layout()

        # Display the image
        self.im = self.ax.imshow(im, origin="lower", cmap="gray", interpolation="Hanning")

        self.plot = helper_GUI.QtG.QDialog(self)
        self.plot.canvas = helper_GUI.plt_qtbackend.FigureCanvasQTAgg(self.fig)
        self.plot.canvas.mpl_connect("button_press_event", self.onclick)
        self.plot.canvas.mpl_connect("key_press_event", self.myKeyPressEvent)
        self.plot.canvas.setFocusPolicy(helper_GUI.QtCore.Qt.ClickFocus)
        self.plot.canvas.setFocus()
        self.plot.canvas.mpl_connect("button_release_event", self.onrelease)
        self.plot.canvas.mpl_connect("motion_notify_event", self.onmove)
        #self.plot.canvas.mpl_connect("resize_event", self.onresize)
        self.plot.canvas.mpl_connect("draw_event", self.ondraw)
        self.plot.toolbar = self.create_plot_toolbar()

        layout = helper_GUI.QtG.QVBoxLayout()
        layout.addWidget(self.plot.toolbar)
        layout.addWidget(self.plot.canvas)

        self.plot.setLayout(layout)
        self.plot.canvas.draw()
        self.plot.show()
        self.background_current = self.fig.canvas.copy_from_bbox(self.ax.bbox)

    @abstractmethod
    def create_plot_toolbar(self):
        pass

    @abstractmethod
    def picking_filament_changed(self):
        pass

    @abstractmethod
    def searchRange_label_changed(self):
        pass

    @abstractmethod
    def searchRange_changed(self):
        pass

    @abstractmethod
    def event_image_changed(self):
        pass

    @abstractmethod
    def show_size_distribution(self):
        pass

    @abstractmethod
    def show_confidence_histogram(self):
        pass

    @abstractmethod
    def close_boxmanager(self):
        pass

    @abstractmethod
    def open_SPA_folder(self):
        pass

    @abstractmethod
    def open_SPA_image(self):
        pass

    @abstractmethod
    def open_tomo_folder(self):
        pass

    @abstractmethod
    def open_tomo_image(self):
        pass

    @abstractmethod
    def import_box_files(self):
        pass

    @abstractmethod
    def save_on_files(self):
        pass

    @abstractmethod
    def apply_filter(self):
        pass

    @abstractmethod
    def box_size_changed(self):
        pass

    @abstractmethod
    def box_distance_filament_changed(self):
        pass

    @abstractmethod
    def visualization_changed(self):
        pass

    @abstractmethod
    def use_estimated_size_changed(self):
        pass

    @abstractmethod
    def lower_size_thresh_changed(self):
        pass

    @abstractmethod
    def lower_size_label_changed(self):
        pass

    @abstractmethod
    def upper_size_thresh_changed(self):
        pass

    @abstractmethod
    def upper_size_label_changed(self):
        pass

    @abstractmethod
    def conf_thresh_changed(self):
        pass

    @abstractmethod
    def conf_thresh_label_changed(self):
        pass

    @abstractmethod
    def memory_changed(self):
        pass

    @abstractmethod
    def memory_label_changed(self):
        pass

    @abstractmethod
    def min_length_changed(self):
        pass

    @abstractmethod
    def min_length_label_changed(self):
        pass

    @abstractmethod
    def min_edge_weight_changed(self):
        pass

    @abstractmethod
    def min_edge_weight_label_changed(self):
        pass

    @abstractmethod
    def win_size_changed(self):
        pass

    @abstractmethod
    def win_size_label_changed(self):
        pass

    @abstractmethod
    def preview(self):
        pass

    @abstractmethod
    def trace(self):
        pass

    @abstractmethod
    def onclick(self, event:helper_GUI.plt_qtbackend):
        pass

    @abstractmethod
    def myKeyPressEvent(self, event:helper_GUI.plt_qtbackend):
        pass

    @abstractmethod
    def onrelease(self, event:helper_GUI.plt_qtbackend):
        pass

    @abstractmethod
    def onmove(self, event:helper_GUI.plt_qtbackend):
        pass

    #todo: still to implement in the old version too, not understand the user case
    @abstractmethod
    def onresize(self):
        pass

    @abstractmethod
    def ondraw(self, event:helper_GUI.plt_qtbackend):
        pass

    # wrapper for function defined in helperGUI but used in other function.
    @abstractmethod
    def clicked_cancel(self):
        """
        Return the QT value after clicking on Cancel
        """
        return helper_GUI.QtG.QMessageBox.Cancel

    @abstractmethod
    def clicked_yes(self):
        """
        Return the QT value after clicking on Yes
        """
        return helper_GUI.QtG.QMessageBox.Yes

    @abstractmethod
    def warning_retrain(self):
        """
        Show warning message 'Only the file saved in 'CBOX_UNTRACED' are usable to retrain crYOLO'
        """

        helper_GUI.QtG.QMessageBox.warning(self, "Info",
                                       "Only the file saved in 'CBOX_UNTRACED' are usable to retrain crYOLO")

    @abstractmethod
    def checkbox_state_value(self, checked:bool)->QT:
        """
        Returns the checked state value of the checkbox
        :param checked: True returns
        """
        return helper_GUI.QtCore.Qt.Checked if checked else helper_GUI.QtCore.Qt.Unchecked

    @abstractmethod
    def create_progress_dialog(self, title):
        """
        Return progress dialog object
        :param title: title to show in the progress dialog window
        """
        return helper_GUI.QtG.QProgressDialog(title, "Cancel", 0, 100, self)


    @abstractmethod
    def display_default_params(self):
        helper_GUI.display_default_params(view=self)

    @abstractmethod
    def tracing_tab_blurring(self, is_enable:bool, has_filament:bool):
        helper_GUI.tracing_tab_blurring(view=self, is_enable=is_enable, has_filament=has_filament)

    @abstractmethod
    def blur_estimated_size(self):
        self.use_estimated_size_checkbox.setEnabled(False)
        self.use_estimated_size_label.setEnabled(False)

    @abstractmethod
    def thresholding_tab_blurring_(self, is_enable:bool, kind_of_cbox:bool, has_filament:bool, type_case:int)->None:
        """
        After loading from file we have to unblur some options in thresholding tabs
        :param is_enable: If True enable SOME options. If False disable ALL the options
        :param kind_of_cbox: True if model.is_cbox or model.is_cbox_untracved is True
        :param has_filament: If True we work with filament
        :param type_case: constants.Type_case. value
        """
        helper_GUI.thresholding_tab_blurring_(self, is_enable=is_enable, kind_of_cbox=kind_of_cbox, has_filament=has_filament, type_case=type_case)

    @abstractmethod
    def update_low_up_thresh(self, max_size:int, min_size:int) -> None:
        """
        After loading from file we have to update upper and lower threshold values
        :param max_size: max size value
        :param min_size: min size value
        """
        helper_GUI.update_low_up_thresh(self,max_size=max_size, min_size=min_size)

    @abstractmethod
    def apply_to_all_the_tomo_question(self, name_param:str)->int:
        return helper_GUI.apply_to_all_the_tomo_question(self,name_param=name_param)

    @abstractmethod
    def err_message(self, msg:str)->None:
        helper_GUI.err_message(self,msg=msg)

    @abstractmethod
    def qt_esixting_folder(self, msg:str)->str:
        return helper_GUI.qt_esixting_folder(self,msg=msg)

    @abstractmethod
    def qtmessage(self, msg:str,has_cancel:bool)->int:
        return helper_GUI.qtmessage(self,msg=msg, has_cancel=has_cancel)

    @abstractmethod
    def get_selected_folder(self, unsaved_changes:bool)->str:
        return helper_GUI.get_selected_folder(self,unsaved_changes=unsaved_changes)

    @abstractmethod
    def get_selected_file(self, unsaved_changes:bool)->str:
        return helper_GUI.get_selected_file(self,unsaved_changes=unsaved_changes)

    @abstractmethod
    def get_inter_box_distance(self, value:int)->Tuple[int,int]:
        """
        Get inter box distance value before saving the filaments
        :param value: default value displayed after opening the window
        :return new value and result
        """
        return QtG.QInputDialog.getInt(self,"Inter-box distance", "Please set the inter-box distance (in pixel) for each filament:", value=   value)

    @abstractmethod
    def uncheck_all_slides(self,type_case:int)->None:
        """
        Uncheck all the checked checkboxes
        :param type_case: constants.Type_case. value
        """
        helper_GUI.uncheck_all_slides(self,type_case=type_case)

    @abstractmethod
    def set_checkstate_tree_leafs(self,item: QtG.QTreeWidgetItem, entries: List[str], state: QtCore.Qt.CheckState) -> None:
        """
        Check or uncheck the checkboxes in the tree
        :param item: controller.view.tree.invisibleRootItem()
        :param entries: list of entries as strings (e.g.: list of slices)
        :param state: helper_GUI.QtCore.Qt.Checked or helper_GUI.QtCore.Qt.Unchecked
        """
        helper_GUI.set_checkstate_tree_leafs(item=item, entries=entries, state=state)

    @abstractmethod
    def create_tree_widget_item(self,title:str)->QtG.QTreeWidgetItem:
        return helper_GUI.QtG.QTreeWidgetItem([title])

    @abstractmethod
    def check_preview_checkbox(self, check):
        self.preview_checkbox.setCheckState(self.checkbox_state_value(checked=check))

    @abstractmethod
    def check_use_estimated_size_checkbox(self, check):
        self.use_estimated_size_checkbox.setCheckState(self.checkbox_state_value(checked=check))

    @abstractmethod
    def check_item_checkbox(self, item, check:bool)->None:
        """
        The filenames/slices's checkboxes
        """
        item.setCheckState(0,self.checkbox_state_value(checked=check))

    @abstractmethod
    def line_setText(self,line:QtG.QLineEdit,value:str )->None:
        """
        Set the value into the line (e.g: boxsize line)
        """
        line.setText(value)

    @abstractmethod
    def plot_distribution(self, fig: plt.Figure) -> None:
        """
        Shows the Plot statistics
        ;param fig: matplot figure
        """
        plot = helper_GUI.QtG.QDialog(self)
        plot.canvas = helper_GUI.plt_qtbackend.FigureCanvasQTAgg(fig)
        layout = helper_GUI.QtG.QVBoxLayout()
        layout.addWidget(plot.canvas)
        plot.setLayout(layout)
        plot.setWindowTitle("Size distribution")
        plot.canvas.draw()
        plot.show()

    @abstractmethod
    def blur_picking_combobox(self, is_importing:bool, has_filament:bool)->None:
        """
        Blur the picking combobox and set the correct value on it
        :param is_importing: True if we are importing boxes
        :param has_filament: True if we loaded or picking filaments
        """
        if is_importing:
            # check and update picking filament combobox and related vars
            if not has_filament and self.picking_filament_combox.currentText() == constants.Picking_cb.FILAMENT.value or \
                    has_filament and self.picking_filament_combox.currentText() == constants.Picking_cb.PARTICLE.value:
                pick = constants.Picking_cb.FILAMENT if has_filament else constants.Picking_cb.PARTICLE
                self.picking_filament_combox.setCurrentText(pick.value)  # it call 'view.picking_filament_combox.currentIndexChanged.connect(controller.picking_filament_changed)'

        # after loading picking is not possible to switch from picking box and filament. you have to reset
        self.picking_filament_combox.setEnabled(False)

    @abstractmethod
    def set_cbox_visualization(self,  has_filament:bool)->None:
        """
        set circle visualization in case of importing boxes from cbox
        :param has_filament: True if we loaded or picking filaments
        """

        if has_filament and self.visualization_combobox.currentText() != constants.Visualization_cb.CIRCLE_SEGMENTED.value:
            self.visualization_combobox.setCurrentText(constants.Visualization_cb.CIRCLE_SEGMENTED.value)
        elif not has_filament and self.visualization_combobox.currentText() != constants.Visualization_cb.CIRCLE.value:
            self.visualization_combobox.setCurrentText(constants.Visualization_cb.CIRCLE.value)

    @abstractmethod
    def enable_button_apply_filter(self)->None:
        self.button_apply_filter.setEnabled(True)

    @abstractmethod
    def setCurrentItem_viewTree(self,is_tomo_folder:bool, number_tomo:int =0, z:int =0)->None:
        """
        Set the current item of the view's tree
        :param is_tomo_folder: True in case we loaded a folder of tomo
        :parma number_tomo: index of the tomo in the tree
        :param z: number of slice
        """
        # child_1 = folder  child_2 = # tomo  child_3 = # of slice
        if is_tomo_folder:
            self.tree.setCurrentItem(self.tree.invisibleRootItem().child(0).child(number_tomo).child(z))
        else:
            self.tree.setCurrentItem(self.tree.invisibleRootItem().child(number_tomo).child(z))

    @abstractmethod
    def setWindowTitle_viewPlot(self,title:str)->None:
        """
        Set the title of the plot window
        """
        self.plot.setWindowTitle(title)

    @staticmethod
    def run_in_same_thread():
        QtCore.QCoreApplication.instance().processEvents()

    @staticmethod
    def meta_modifier_is_clicked():
        return helper_GUI.QtG.QApplication.keyboardModifiers() == helper_GUI.QtCore.Qt.MetaModifier

    @staticmethod
    def control_modifier_is_clicked():
        return helper_GUI.QtG.QApplication.keyboardModifiers() == helper_GUI.QtCore.Qt.ControlModifier

    @staticmethod
    def fill_root_childs(root: QtG.QTreeWidgetItem, tot_slices: int, is_folder: bool = False,root_child_index: int = None) -> None:
        """
        Creates all the checkboxes of a given tomogram in the GUI
        :param root: The 'QTreeWidgetItem' obj represent the item list (namely the filenames)
        :param tot_slices:  number of slices present in the tomogram
        :param is_folder: True if we loaded a folder of tomo
        :param root_child_index: index of child in root. It is the item, which represent a tomogram in a folder
        """
        helper_GUI.fill_root_childs(root=root, tot_slices=tot_slices, is_folder=is_folder,root_child_index=root_child_index)

    @abstractmethod
    def get_picking_filament_cb_text(self)->str:
        """
        Return the text of the picking filament combobox
        """
        return self.picking_filament_combox.currentText()

    @abstractmethod
    def get_visualization_cb_text(self)->str:
        """
        Return the text of the visualization combobox
        """
        return self.visualization_combobox.currentText()