# flake8: noqa

import pkg_resources


__version__ = pkg_resources.get_distribution("pybsc").version


from pybsc.split import nsplit

from pybsc.iter_utils import pairwise
from pybsc.iter_utils import triplewise

from pybsc.json_utils import load_json
from pybsc.json_utils import save_json

from pybsc.dict_utils import invert_dict

from pybsc.download import download_file

from pybsc.sort_utils import is_sorted

from pybsc.pickle_utils import load_pickle

from pybsc.rm_utils import rm_rf

from pybsc.cache_readline_history import cache_readline

from pybsc.closest_indices import argclosest
