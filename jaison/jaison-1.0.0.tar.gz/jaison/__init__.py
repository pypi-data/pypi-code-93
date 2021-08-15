import os
import logging
logging.getLogger('matplotlib').setLevel(level=logging.WARNING)
from jaison.api import __all__ as api_all_list
from jaison.api import * # noqa
import jaison.data as data
from jaison.data import infer_types, statistical_analysis
from jaison.__about__ import __package_name__ as name, __version__


os.environ['TOKENIZERS_PARALLELISM'] = 'true'
__all__ = ['data', 'infer_types', 'statistical_analysis', 'name', '__version__', *api_all_list]
