"""Root package info."""

__version__ = '0.0.1.dev11'
__author__ = 'SoC Platform Lab'
__author_email__ = 'hwangdonghyun@seoultech.ac.kr'
__license__ = 'GPLv3'
__copyright__ = 'Copyright (c) 2020, %s.' % __author__
__homepage__ = 'https://github.com/Intellino/intellino'

__docs__ = "The Intellino core logic wrapper for ML simulation with intellino"

try:
    # This variable is injected in the __builtins__ by the build
    # process. It used to enable importing subpackages of skimage when
    # the binaries are not built
    __INTELLINO_SETUP__
except NameError:
    __INTELLINO_SETUP__ = False

if __INTELLINO_SETUP__:
    import sys
    sys.stderr.write('Partial import of `intellino` during the build process.\n')
    # We are not importing the rest of the scikit during the build
    # process, as it may not be compiled yet
else:
    from .core.neuron_cell import NeuronCells
    from .utils.data.dataloader import DataLoader
    from .utils.data.dataset import Dataset

    __all__ = [
        'NeuronCells',
        'DataLoader',
        'Dataset',
    ]
    # __call__ = __all__
