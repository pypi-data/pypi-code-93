from napari_plugin_engine import napari_hook_implementation
from napari.utils.colormaps.colormap_utils import AVAILABLE_COLORMAPS
from dexp.datasets.zarr_dataset import ZDataset


@napari_hook_implementation
def napari_get_reader(path):
    """A basic implementation of the napari_get_reader hook specification.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    paths = [path] if isinstance(path, str) else path

    # if we know we cannot read the file, we immediately return None.
    for path in paths:
        if not path.endswith((".zarr", ".zarr.zip")):
            return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


LABELS_KEYWORDS = ('segment', 'instance', 'mask', 'label')


def _guess_layer_type(channel: str) -> str:
    # TODO: propose a better alternative using metadata?
    layer_type = 'image'
    for keyword in LABELS_KEYWORDS:
        if keyword in channel.lower():
            layer_type = 'labels'
            break
    return layer_type


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    paths = [path] if isinstance(path, str) else path

    layer_data = []
    axes = ('dt', 'dz', 'dy', 'dx')

    for path in paths:
        mode = 'r' if path.endswith('.zip') else 'r+'
        dataset = ZDataset(path, mode=mode)
        metadata = dataset.get_metadata()

        ds_scale = [metadata.get(axis, 1.0) for axis in axes]

        for channel in dataset.channels():
            layer_type = _guess_layer_type(channel)

            add_kwargs = {
                'name': channel,
            }

            if layer_type == 'image':
                add_kwargs['blending'] = 'additive'

                for colormap in AVAILABLE_COLORMAPS:
                    if colormap in channel.lower():
                        add_kwargs['colormap'] = colormap

            channel_metadata = metadata.get(channel, {})
            add_kwargs['scale'] = [channel_metadata.get(axis, s) for axis, s in zip(axes, ds_scale)]

            array = dataset.get_array(channel)
            layer_data.append((array, add_kwargs, layer_type))
        
    return layer_data
