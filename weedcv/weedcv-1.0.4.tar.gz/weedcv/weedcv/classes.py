import os


class Params:
    """PlantCV parameters class."""

    def __init__(
        self,
        device=0,
        debug=None,
        debug_filename="debug_results",
        debug_outdir="results/debug",
        line_thickness=5,
        log_path=".",
        dpi=100,
        text_size=0.55,
        text_thickness=2,
        marker_size=60,
        color_scale="gist_rainbow",
        color_sequence="sequential",
        saved_color_scale=None,
        verbose=True,
    ):
        """Initialize parameters.
        Keyword arguments/parameters:
        device            = Device number. Used to count steps in the pipeline. (default: 0)
        debug             = None, print, or plot. Print = save to file, Plot = print to screen. (default: None)
        debug_outdir      = Debug images output directory. (default: .)
        line_thickness    = Width of line drawings. (default: 5)
        dpi               = Figure plotting resolution, dots per inch. (default: 100)
        text_size         = Size of plotting text. (default: 0.55)
        text_thickness    = Thickness of plotting text. (default: 2)
        marker_size       = Size of plotting markers (default: 60)
        color_scale       = Name of plotting color scale (matplotlib colormap). (default: gist_rainbow)
        color_sequence    = Build color scales in "sequential" or "random" order. (default: sequential)
        saved_color_scale = Saved color scale that will be applied next time color_palette is called. (default: None)
        verbose           = Whether or not in verbose mode. (default: True)
        :param device: int
        :param debug: str "save"
        :param debug_outdir: str
        :param line_thickness: numeric
        :param dpi: int
        :param text_size: float
        :param text_thickness: int
        :param marker_size: int
        :param color_scale: str
        :param color_sequence: str
        :param saved_color_scale: list
        :param verbose: bool
        """

        self.device = device
        self.debug = debug
        self.debug_outdir = debug_outdir
        self.debug_filename = debug_filename
        self.line_thickness = line_thickness
        self.log_path = log_path
        self.dpi = dpi
        self.text_size = text_size
        self.text_thickness = text_thickness
        self.marker_size = marker_size
        self.color_scale = color_scale
        self.color_sequence = color_sequence
        self.saved_color_scale = saved_color_scale
        self.verbose = verbose
