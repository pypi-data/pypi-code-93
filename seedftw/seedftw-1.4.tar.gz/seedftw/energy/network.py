"""
Functions related to modelling of energy networks.

This file can also be imported as a module and contains the following
functions:

    * split_import_export - split timeseries of import and export


"""

from typing import Tuple
import numpy as np
import pandas as pd


def split_import_export(net_import: pd.Series) -> Tuple[pd.Series, pd.Series]:
    """Models the power production curve of a standard wind turbine.
    The model is based upon (Twidell, 2006), pp. 306-307.

    Parameters
    ----------
    net_import : np.array or Series
        Values of the net import (i.e. >0 is import, <0 is export)

    Raises
    ------
    None

    Returns
    -------
    imports : np.array, Series or pd.DataFrame
        Timeseries of imports
    exports : np.array, Series or pd.DataFrame
        Timeseries of exports
    """

    if net_import is None:
        imports = None
        exports = None
    elif all(v is None for v in net_import):
        imports = net_import
        exports = net_import
    else:
        imports = np.fmax(net_import, [0])
        exports = np.fmax(-net_import, [0])

    return imports, exports
