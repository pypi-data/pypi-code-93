from .._tier0 import plugin_function
from .._tier0 import Image
from .._tier0 import push
from .._tier1 import replace_intensities
from .._tier1 import set_column

@plugin_function(categories=['combine', 'label measurement', 'map', 'in assistant'], priority=-1)
def label_standard_deviation_intensity_map(intensity_image : Image, labels : Image, standard_deviation_intensity_map : Image = None):
    """Takes an image and a corresponding label map, determines
    the standard deviation of the intensity per label and replaces
    every label with the that number.

    This results in a parametric image expressing standard
    deviation of object intensity.

    Parameters
    ----------
    intensity_image
    labels
    standard_deviation_intensity_map

    Returns
    -------

    References
    ----------
    .. [1] https://clij.github.io/clij2-docs/reference_standardDeviationIntensityMap
    """
    from .._tier9 import statistics_of_background_and_labelled_pixels
    from .._tier9 import push_regionprops_column

    regionprops = statistics_of_background_and_labelled_pixels(intensity_image, labels)

    values_vector = push_regionprops_column(regionprops, "standard_deviation_intensity")
    set_column(values_vector, 0, 0)

    standard_deviation_intensity_map = replace_intensities(labels, values_vector, standard_deviation_intensity_map)

    return standard_deviation_intensity_map
