from enum import Enum

# unique id used to identify the center of a filamente during the picking phase
CENTER_LINE_ID = "invelid"

class Writer_filament_suffix(Enum):
    """
    List of suffix of output folder in the filament cases
    """
    HELICON_SUFFIX = "_HELICON"
    CBOX_FILAMENT_SUFFIX = "_FILAMENT"
    EMAN_STAR_FILAMENT_SUFFIX = "_START_END"


class Slider_release_fcall(Enum):
    """
    List of function call to map in changed_slider_release to run the related controller's function
    the boxmanager main win
    """
    CONF = 0
    LOWER_SIZE = 1
    UPPER_SIZE = 2
    # num_boxes , last thresholding option
    SEARCH_RANGE = 4
    MEMORY = 5
    MIN_LENGTH = 6
    MIN_EDGE_W = 7
    WIN_SIZE = 8


class Picking_cb(Enum):
    """
    List of possible picking choices present in the 'picking' combobox in the boxmanager main win
    """
    PARTICLE = 'Particle'
    FILAMENT = 'Filament'


class Visualization_cb(Enum):
    """
    List of possible visualization choices present in the 'visualization'' combobox in the 'visualization' tab in
    the boxmanager main win
    """
    CIRCLE = 'Circle'
    RECT = 'Rectangle'

    # value for the filament visualization
    CIRCLE_SEGMENTED = 'Circle (Filament Segmented)'  # list of cirlces
    RECT_FILAMENT_SEGMENTED = 'Rectangle (Filament Segmented)'  # list of rectangles
    RECT_FILAMENT_START_END = 'Rectangle (Filament Start-end)'  # single rectangle

class Type_case(Enum):
    """
    Identify if the loaded case is SPA, single tomo or folder of tomo
    """
    NOT_LOADED = None
    SPA = 0
    TOMO = 1
    TOMO_FOLDER = 2

class Filetype_name(Enum):
    """
    Map the filetype with values used to read the image via 'helper.read_image'
    """
    JPG = 0
    JPEG = 0
    TIF = 1
    TIFF = 1
    MRC = 2
    MRCS = 2
    REC =2


class Default_settings_value(Enum):
    """
    List of the default setting values
    """
    # default value for the picking combobox not present in any tabs
    PICKING_CB = Picking_cb.PARTICLE.value

    # default value for the 'Visualization' tab
    DEFAULT_BOX_SIZE = 200
    DEFAULT_BOX_DISTANCE_FILAMENT_SIZE = int(DEFAULT_BOX_SIZE / 10)
    VISUALIZATION_CB = Visualization_cb.CIRCLE.value

    # default value for the 'Thresholding' tab
    DEFAULT_UPPER_SIZE_THRESH = 99999
    DEFAULT_LOWER_SIZE_THRESH = 0
    DEFAULT_CURRENT_CONF_THRESH = 0.3
    DEFAULT_CURRENT_NUM_BOXES_THRESH = 0
    DEFAULT_MIN_NUM_BOXES_THRESH = 0
    DEFAULT_MAX_NUM_BOXES_THRESH = 100
    DEFAULT_MIN_EDGE_WEIGHT = 0.4

    # default value for the 'Filtering' tab
    DEFAULT_FILTER_FREQ = 0.1

    # default value for the 'Tracing' tab
    DEFAULT_SEARCH_RANGE = 5
    DEFAULT_MEMORY = 0
    DEFAULT_MIN_LENGTH = 5
