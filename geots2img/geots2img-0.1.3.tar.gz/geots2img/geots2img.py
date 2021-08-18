import warnings
import copy
import numpy as np
import os
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
import pytz


class ImageGenerator:
    """ Generates an image based on a number of individual data points """

    def __init__(self, x_range, y_range, resolution):
        """
        :param x_range:  array of [float, float] indicating min, max of x range
        :param y_range:  array of [float, float] indicating min, max of y range
        :param resolution: float indicating discretisation interval size
        """

        self.x_range = x_range                  # [min, max] x values
        self.y_range = y_range                  # [min, max] y values
        self.resolution = resolution            # discretisation interval

        self.source_points = []                 # list of tuples (x, y) for source points
        self.source_values = []                 # list of values at source points (must be in same order)

        self.points_per_boundary = 5            # How many points should be generated at each boundary
        self.boundary_points = []               # list of tuples (x, y) for boundary points
        self.boundary_values = []               # list of values at boundary points (must be in same order)
        self.generate_boundary_points()

        self.fitted_values = None   # 2D numpy array: values in full grid after fitting a surface

        self.cmap = plt.get_cmap('cividis')     # color map to use
        self.image = None           # PIL Image generated using fitted_values

        # Create coordinate grid
        self.grid_x, self.grid_y = np.mgrid[
                                   self.x_range[0]: self.x_range[1]: self.resolution,
                                   self.y_range[0]: self.y_range[1]: self.resolution
                                   ]

    def _check_points_valid(self, points):
        """
        Helper function that checks if source / boundary points are in valid ranges, and issues warnings if not
        @param points: list of tuple (x, y, value) where x,y define location and value is in range [0,1]
        @return: None
        """
        for p in points:
            if not (self.x_range[0] <= p[0] <= self.x_range[1]):
                warning_str = f"Value {p[0]} not in range {self.x_range}"
                warnings.warn(warning_str, UserWarning)
            if not (self.y_range[0] <= p[1] <= self.y_range[1]):
                warning_str = f"Value {p[1]} not in range {self.y_range}"
                warnings.warn(warning_str, UserWarning)

    def _check_values_valid(self, values):
        """
        Helper function that checks if values are in valid ranges, and issues warnings if not
        @param values: list of values expected to be in range [0,1]
        @return: None
        """
        for v in values:
            if not (0 <= v <= 1):
                warning_str = f"Value {v} not in range {[0, 1]}"
                warnings.warn(warning_str, UserWarning)

    def set_source_points(self, source_points):
        """
        Set source points (overwrites any existing source points)
        @param source_points: list of tuple (x, y)
        @return: None
        """
        self._check_points_valid(source_points)
        self.source_points = source_points

    def set_source_values(self, source_values):
        """
        Set source values
        :param source_values: list of floats, must be in same order as self.source_points
        :return: None
        """
        self._check_values_valid(source_values)
        self.source_values = source_values

    def set_boundary_points(self, boundary_points):
        """
        Set boundary points (overwrites any existing boundary points)
        @param boundary_points: list of tuple (x, y)
        @return: None
        """
        self._check_points_valid(boundary_points)
        self.boundary_points = boundary_points

    def set_boundary_values(self, boundary_values):
        """
        Set boundary values
        :param boundary_values: list of floats, must be in same order as self.boundary_points
        :return: None
        """
        self._check_values_valid(boundary_values)
        self.boundary_values = boundary_values

    def generate_boundary_points(self):
        """ Generate synthetic points along boundary of image """
        boundary_points = []
        boundary_x = np.linspace(self.x_range[0], self.x_range[1], num=self.points_per_boundary)
        boundary_y = np.linspace(self.y_range[0], self.y_range[1], num=self.points_per_boundary)

        # Add top and bottom edges
        for x in boundary_x:
            boundary_points.append([x, boundary_y[0]])
            boundary_points.append([x, boundary_y[-1]])
        # Add left and right edges
        for y in boundary_y:
            boundary_points.append([boundary_x[0], y])
            boundary_points.append([boundary_x[-1], y])

        self.boundary_points = boundary_points

    def generate_boundary_values(self):
        """
        Generate values of boundary points using current values of source points.
        For now, the method for choosing boundary values is simply to use value of nearest source point.
        """
        if len(self.boundary_points) == 0:
            raise BaseException("Cannote generate boundary values when there are no boundary points")
        if len(self.source_values) == 0:
            raise BaseException("Cannot generate boundary values when there are no source values")

        # Determine value of each point using nearest source point
        source_xy = [[p[0], p[1]] for p in self.source_points]
        boundary_x = [p[0] for p in self.boundary_points]
        boundary_y = [p[1] for p in self.boundary_points]
        self.boundary_values = griddata(source_xy, self.source_values,
                                        (boundary_x, boundary_y),
                                        method='nearest').ravel()

    def set_color_map(self, cmap):
        """ Set the color map """
        self.cmap = cmap

    def generate_fitted_values(self, include_boundary_points=True):
        """ Generate values for entire grid using source and boundary points """
        if len(self.source_points) == 0:
            raise BaseException("Cannot generate fitted values if there are no source points")
        all_points = self.source_points
        all_values = self.source_values

        # If we want to include boundary points
        if include_boundary_points:
            self.generate_boundary_values()
            all_points = np.append(all_points, self.boundary_points, axis=0)
            all_values = np.append(all_values, self.boundary_values)

        # Finally generate fitted values
        self.fitted_values = griddata(all_points, all_values, (self.grid_x, self.grid_y), method='cubic')

    def get_fitted_values(self, refit=False):
        """
        Retrieve all fitted values (full grid).  Note that if values have not been fitted, returns None.
        :param refit: boolean indicating whether to force refit of surface (even if one has already been fitted)
        :return: 2D numpy array with all fitted values
        """
        # Do we want to force refit?
        if refit:
            self.generate_fitted_values()

        return self.fitted_values

    def get_fitted_point_values(self, points, refit=False):
        """
        Retrieve values at each of the provided points after having fitting a surface
        @param points: array of (float, float), pairs of x, y -- specifying points to return values for
        @param refit: boolean indicating whether to force refit of surface (even if one has already been fitted)
        @return: array of float, indicating values at those points after surface fitting
        """
        if refit or (self.fitted_values is None):
            self.generate_fitted_values()

        fitted_point_values = []
        for point in points:
            # Convert to coordinates used in grid of fitted values
            x_index = int((point[0] - self.x_range[0]) / self.resolution)
            y_index = int((point[1] - self.y_range[0]) / self.resolution)
            fitted_point_values.append(self.fitted_values[x_index, y_index])

        return fitted_point_values

    def generate_image(self, include_boundary_points=True, flip_y=True, refit=False):
        """
        Generate an image using existing class data and settings
        @param include_boundary_points: bool (default True), whether to include boundary points
        @param flip_y: bool (default True), whether to flip image across y-axis
        @param refit: bool (default False), whether to force refitting of values
        @return: None
        """
        if len(self.source_points) == 0 or len(self.source_values) == 0:
            raise BaseException("Cannot generate image when there are no source points or no source values")

        # Ensure we have fitted values
        if refit or (self.fitted_values is None):
            self.generate_fitted_values(include_boundary_points=include_boundary_points)

        grid_z_values = copy.copy(self.fitted_values)

        # If color map specified, convert to this
        if self.cmap is not None:
            grid_z_values = np.uint8([x * 255 for x in self.cmap(grid_z_values)])

        # Due to differing coordinate systems between np and PIL, must swap axes
        grid_z_values = np.swapaxes(grid_z_values, 0, 1)

        # Flip y axis?  This is common for images, where data is usually represented top to bottom
        if flip_y:
            grid_z_values = np.flip(grid_z_values, 0)

        self.image = Image.fromarray(grid_z_values)

    def save_image(self, save_path):
        """ Save the image at specified path """

        if self.image is None:
            raise BaseException("No image exists.  Generate image before trying to save.")

        # Ensure that the directory exists (and create it if it doesn't)
        head, tail = os.path.split(save_path)
        Path(head).mkdir(parents=True, exist_ok=True)

        # Save image
        self.image.convert('RGB').save(save_path)


def generate_image_sequence(data,
                            image_gen,
                            time_window=None,
                            save_path=None,
                            filename_format='numerical'):
    """
    Generate a sequence of images using an image generator for a given dataset
    :param data: pandas dataframe having timestamps as index, and one column per time series
    :param time_window: [timestamp, timestamp] indicating interval over which to generate images
    :param image_gen: ImageGenerator object.  Source points must already be set.
    :param save_path: string, path to where images should be saved
    :param filename_format: string indicating filename format, either 'timestamp', or 'datetime'
    :return: None
    """

    # Set intervals that we should loop over
    if time_window is None:
        timestamps = data.index
    else:
        timestamps = data[time_window[0]:time_window[1]].index

    # Handle empty save path
    if save_path is None:
        save_path = "images/"

    # Maintain loop counter in case we need to save files using numerical format filenames
    loop_ix = 1
    for curr_time in timestamps:
        # Get this interval's values
        image_gen.set_source_values(np.array(data.loc[curr_time].values))

        # Generate image
        image_gen.generate_image(refit=True)

        # Save image
        filename_base = ""
        if filename_format == 'timestamp':
            # Use UTC
            utc_time = curr_time.astimezone(pytz.utc)
            filename_base = utc_time.strftime('%Y-%m-%d_%H-%M-%S')
        elif filename_format == 'numerical':
            filename_base = '{:08d}'.format(loop_ix)
        image_gen.save_image(f"{save_path}{filename_base}.jpg")

        loop_ix += 1


def generate_video(source_path, target_path=None, frame_rate=30, output_format='mp4'):
    """
    Simple python wrapper for command line ffmpeg tool to generate a video of existing image sequence
    :param source_path: Where to find image sequence files (must have 8-digit numbered filenames, e.g. 00000001.jpg)
    :param target_path: Where to save the video, default "_video.mp4"
    :param frame_rate: int indicating framerate, default 30
    :param output_format: string indicating preferred output format.  Currently only mp4 and gif supported.
    """
    """  """
    try:
        if output_format == 'mp4':
            if target_path is None:
                target_path = f"{source_path}_video.mp4"
            os.system(f"ffmpeg -r {frame_rate} -i {source_path}%08d.jpg -vcodec mpeg4 -y {target_path}")
        elif output_format == 'gif':
            if target_path is None:
                target_path = f"{source_path}_video.gif"
            os.system(f"ffmpeg -r {frame_rate} -i {source_path}%08d.jpg -f gif -y {target_path}")
    except BaseException:
        raise RuntimeError("Could not generate video, perhaps since ffmpeg is not installed.")
