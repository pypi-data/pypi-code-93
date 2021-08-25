from cryoloBM import constants,box_dictionary,helper
from cryoloBM import MySketch   # for type hinting purpose
from typing import List

class Boxmanager_model:
    def __init__(self, image_dir:str, box_dir:str, wildcard:str, is_tomo:bool)->None:
        self.box_dir = box_dir
        self.wildcard = wildcard
        self.is_tomo =is_tomo
        self.unsaved_changes = False
        self.current_image_path = None
        self.image_folder_path = image_dir

        # the filament we are picking in real time
        self.current_pick_filament = None

        # if we are trying to remove a filemant (otherwise onrelease ll create a new one)
        self.removing_picked_filament = False

        self.trace_all = False

        # helper var used for moving an already existing sketch into the image
        self.moving_box = None
        self.is_moving = False      # True when start to move the moving_box. Before setting to True delete the sketch from the 3D particles (in tomo case

        # identifies if the loaded case is SPA, single tomo or folder of tomo
        self.type_case = constants.Type_case.NOT_LOADED.value

        self.use_estimated_size = False

        # tomo var
        self.current_tomoimage_mmap = None        # it contains a numpy array
        self.index_tomo = None
        self.last_index_tomo = None
            # k= tomo_filename. Contains the values for the 'tracing' parameters silder
        self.smallest_image_dim = dict()
        self.tot_frames = dict()

        # in the folder case it keeps the var params (e.g.: confidence threshold)     for each tomo
        self.params = dict()

        # info about the imported boxes:
            # The 'est_size' instance of a Sketch Class contains the estimated size of cryolo
            # when loaded from '.cbox', and should be never changed
        self.est_box_from_cbox = None   # est_size got from cryolo
        self.is_cbox = False            # the data are in cbox format
        self.is_cbox_untraced = False   # the data are in cbox format and represent untraced particles/filaments
        self.has_filament = False       # the data are filament
        self.has_3d = False             # the 3D visualization is available (only cbox tomo cases. when untraced box are not loaded)

        # it ll be a obj 'Box_dictionary' and it ll manage the sketches in all the images and their conversions
        self.box_dictionary = None

        # If True the current boxes will be hidden. Activated pressing 'h'
        # it is still possible to pick. Until we do not press 'h' again only the new picked sketches ll be drawn
        # in case of changing image it will be deactivated
        self.toggle = False

        # list of sketches to visualize. Ideally it contains the rectangles present in the current image/slice.
        # It is basically a reference, hence changing it you change both, of Box_dictionary.box_dictionary var
        # At usual it is fill with Box_dictionary.get_sketches
        self.rectangles = list()

        self.picking_combobox_value = constants.Picking_cb.PARTICLE.value

        # tab visualization vars
        self.visualization = constants.Visualization_cb.RECT.value
        self.boxsize = constants.Default_settings_value.DEFAULT_BOX_SIZE.value
        self.box_distance_filament = constants.Default_settings_value.DEFAULT_BOX_DISTANCE_FILAMENT_SIZE.value

        # tab thresholding vars
        self.current_conf_thresh = constants.Default_settings_value.DEFAULT_CURRENT_CONF_THRESH.value
        self.lower_size_thresh = constants.Default_settings_value.DEFAULT_LOWER_SIZE_THRESH.value
        self.upper_size_thresh = constants.Default_settings_value.DEFAULT_UPPER_SIZE_THRESH.value
        self.current_num_boxes_thresh = constants.Default_settings_value.DEFAULT_CURRENT_NUM_BOXES_THRESH.value

        # tab filtering vars
        self.filter_freq = constants.Default_settings_value.DEFAULT_FILTER_FREQ.value

        # tab tracing vars
        self.search_range =constants.Default_settings_value.DEFAULT_SEARCH_RANGE.value
        self.memory = constants.Default_settings_value.DEFAULT_MEMORY.value
        self.min_length = constants.Default_settings_value.DEFAULT_MIN_LENGTH.value
        self.min_edge_weight = constants.Default_settings_value.DEFAULT_MIN_EDGE_WEIGHT.value
        self.win_size = constants.Default_settings_value.DEFAULT_BOX_SIZE.value

    def set_rectangles(self, rectangles:List[MySketch.MySketch])->None:
        """
        Fill the rectangles var
        :param rectangles: list of Sketches
        """
        self.rectangles = rectangles

    def clean_box_dictionary(self)->None:
        """
        Clean the box_dictionary var.
        It is used only after opening images. Otherwise i could have the entries of the old case
        """
        if isinstance(self.box_dictionary,box_dictionary.Box_dictionary):
            self.box_dictionary.clean()

    def init_box_dictionary(self, onlyfiles:List[str], tot_slices:int = None)->None:
        """
        Init the box_dictionary variable
        :param onlyfiles: list of the files present in the folder, single file (into a var list)in case of TOMO
        :param tot_slices: number of slices present in the TOMO. Only constants.Type_case.TOMO case
        """
        if self.type_case == constants.Type_case.NOT_LOADED.value:
            exit()
        self.box_dictionary = box_dictionary.Box_dictionary(type_case=self.type_case, onlyfiles=onlyfiles, tot_slices=tot_slices)

    def set_tomo_vars(self)->None:
        """
        Set the tomo vars after opening a tomo or a folder of tomos
        """
        self.index_tomo =0
        self.last_index_tomo = 0
        self.current_tomoimage_mmap = None  # i reset it when i open a new image/folder of
        self.smallest_image_dim = dict()
        self.tot_frames = dict()


    def get_filter_state(self)->tuple:
        return self.lower_size_thresh,self.upper_size_thresh,self.current_conf_thresh

    def get_threshold_params(self, filename:str = None)->tuple:
        """
        Return the param for the current image
        :param filename: in folder case i have to specify from which file, if None returns those of the current case
        :return the 4 threshold settable from the visualization's tab
        """
        if self.type_case == constants.Type_case.TOMO_FOLDER.value and filename:
            p = self.params[filename]
            return p.conf_thresh, p.upper_size_thresh, p.lower_size_thresh, p.num_boxes_thresh
        return self.current_conf_thresh, self.upper_size_thresh, self.lower_size_thresh, self.current_num_boxes_thresh


    def fill_params(self,list_files:List[str])->None:
        """
        filter_freq, upper_size_thresh, lower_size_thresh, conf_thresh, min_num_boxes_thresh,
                 max_num_boxes_thresh, min_edge_weight,
                 search_range, memory, min_length
        """
        for f in list_files:
            self.params.update({f: helper.Params(f, constants.Default_settings_value.DEFAULT_FILTER_FREQ.value, constants.Default_settings_value.DEFAULT_BOX_SIZE.value, constants.Default_settings_value.DEFAULT_UPPER_SIZE_THRESH.value, constants.Default_settings_value.DEFAULT_LOWER_SIZE_THRESH.value,
                                          constants.Default_settings_value.DEFAULT_CURRENT_CONF_THRESH.value, constants.Default_settings_value.DEFAULT_CURRENT_NUM_BOXES_THRESH.value,
                                          constants.Default_settings_value.DEFAULT_MIN_EDGE_WEIGHT.value, constants.Default_settings_value.DEFAULT_SEARCH_RANGE.value,
                                          constants.Default_settings_value.DEFAULT_MEMORY.value, constants.Default_settings_value.DEFAULT_MIN_LENGTH.value, constants.Default_settings_value.DEFAULT_BOX_SIZE.value)})

    def reset_config(self)->None:
        """
        Restore the initial values of the model. It is called after clicking 'File-Reset'
        """
        self.unsaved_changes = False
        self.rectangles = list()
        self.moving_box = None
        self.is_moving = False

        self.current_pick_filament = None
        self.removing_picked_filament = False

        # In case of loading new images it ll be overwritten in the open function (e.g.:open_tomo_folder)
        if self.box_dictionary:
            self.box_dictionary.reset()

        # The following three parameters are filled via cml hence when we reset they ll be set to None
        self.box_dir = None
        self.wildcard = None
        self.is_tomo = None

        self.use_estimated_size = False

        # info about the imported boxes:
        self.is_cbox = False
        self.is_cbox_untraced = False
        self.has_filament = False
        self.est_box_from_cbox = None

        self.toggle = False

        self.picking_combobox_value = constants.Picking_cb.PARTICLE.value

        # tab visualization vars
        self.visualization = constants.Visualization_cb.RECT.value
        self.boxsize = constants.Default_settings_value.DEFAULT_BOX_SIZE.value
        self.box_distance_filament = constants.Default_settings_value.DEFAULT_BOX_DISTANCE_FILAMENT_SIZE.value

        # tab thresholding vars
        self.current_conf_thresh = constants.Default_settings_value.DEFAULT_CURRENT_CONF_THRESH.value
        self.lower_size_thresh = constants.Default_settings_value.DEFAULT_LOWER_SIZE_THRESH.value
        self.upper_size_thresh = constants.Default_settings_value.DEFAULT_UPPER_SIZE_THRESH.value
        self.current_num_boxes_thresh = constants.Default_settings_value.DEFAULT_CURRENT_NUM_BOXES_THRESH.value

        # tab filtering vars
        self.filter_freq = constants.Default_settings_value.DEFAULT_FILTER_FREQ.value

        # tab tracing vars
        self.search_range =constants.Default_settings_value.DEFAULT_SEARCH_RANGE.value
        self.memory = constants.Default_settings_value.DEFAULT_MEMORY.value
        self.min_length = constants.Default_settings_value.DEFAULT_MIN_LENGTH.value
        self.min_edge_weight = constants.Default_settings_value.DEFAULT_MIN_EDGE_WEIGHT.value
        self.win_size = constants.Default_settings_value.DEFAULT_BOX_SIZE.value

        self.trace_all = False

        # The following vars will be not reset:
        # self.type_case
        #   no reset the next 2 vars, otherwise after resetting we cannot change image
        #self.current_image_path = None
        #self.image_folder_path = None
        # no reset the tomo var too , otherwise after resetting we cannot change image (because it crashes)
        #self.index_3D_tomo = None
        #self.last_index_3D_tomo = None
        #self.current_tomoimage_mmap = None

        # self.has_3d = False