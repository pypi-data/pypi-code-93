# Functions for reading IDL XPad save files

"""
    from user_functions import *
    data = read_padsav("12354-omv110-FFTP.padsav")[0]
    plot(data)
"""

from numpy import linspace, rollaxis
from scipy.io import readsav
from warnings import catch_warnings, simplefilter
from .pyxpad_utils import XPadDataItem, XPadDataDim


def read_padsav(file_name, disable_UserWarnings=True):
    """
    Reads data from an idl_dict object into XPadDataItem objects

    Parameters
    ----------
    file_name : str
        Path to XPad*.padsav file


    Returns
    -------
    items : list
        A list of XPadDataItems
    """

    warning_action = "default"
    if disable_UserWarnings:
        warning_action = "ignore"

    with catch_warnings():
        simplefilter(warning_action, UserWarning)
        idl_dict = readsav(file_name)

    return parse_padsav(idl_dict)


def parse_padsav(xpad_idl_dict):
    """
    Reads data from an idl_dict object into XPadDataItem objects

    Parameters
    ----------
    xpad_idl_dict : AttrDict or dict
        Input dict from an XPad *.padsav imported using scipy.io.readsav


    Returns
    -------
    items : list
        A list of XPadDataItems
    """

    if not check_padsav(xpad_idl_dict):
        return None

    items = []
    for trace in xpad_idl_dict["ptr"]:
        item = XPadDataItem()

        item.name = trace["NAME"][0]
        item.source = trace["SOURCE"][0]
        item.label = trace["DINFO"][0]["LABEL"][0]
        item.units = trace["DINFO"][0]["UNITS"][0]

        numdims = trace["SIZE"][0][0]

        item.data = rollaxis(trace["DATA"][0], numdims - 1)

        if numdims > 0:
            # f(t), f(t,x) or f(t,x,y)
            dim = XPadDataDim()

            # If we have a time domain, use data from TINFO
            if trace["TINFO"][0]["DOMAINS"][0] > 0:
                dim.data = linspace(
                    trace["TINFO"][0]["START"][0],
                    trace["TINFO"][0]["FINISH"][0],
                    trace["TINFO"][0]["LENGTH"],
                )
            else:
                dim.data = trace["TIME"][0]

            dim.name = trace["TINFO"][0]["LABEL"][0]
            dim.label = dim.name
            dim.units = trace["TINFO"][0]["UNITS"][0]

            item.dim.append(dim)

            item.order = len(item.dim) - 1
            item.time = item.dim[item.order].data

        if numdims > 2:
            # f(t,x,y)
            dim = XPadDataDim()
            dim.data = trace["Y"][0]
            dim.name = trace["YINFO"][0]["LABEL"][0]
            dim.label = dim.name
            dim.units = trace["YINFO"][0]["UNITS"][0]

            item.dim.append(dim)

        if numdims > 1:
            # f(t,x) or f(t,x,y)
            dim = XPadDataDim()
            dim.data = trace["X"][0]
            dim.name = trace["XINFO"][0]["LABEL"][0]
            dim.label = dim.name
            dim.units = trace["XINFO"][0]["UNITS"][0]

            item.dim.append(dim)

        item.desc = trace["TYPE"][0]

        items.append(item)

    return items


def check_padsav(xpad_idl_dict):
    """
    Verifies padsav data and its containing traces are valid.

    Parameters
    ----------
    xpad_idl_dict : AttrDict or dict
        An XPad *.padsav imported using scipy.io.readsav


    Returns
    -------
    int : 0 for invalid, 1 for valid
    """
    if not isinstance(xpad_idl_dict, dict):
        return 0

    if "ptr" not in xpad_idl_dict:
        return 0

    # [*] 'ptr not found in xpad_idl_dict'
    if not xpad_idl_dict["ptr"].size:
        return 0

    for trace in xpad_idl_dict["ptr"]:
        # [*] failed on trace
        if not check_trace(trace):
            return 0

    return 1


def check_trace(xpad_idl_trace):
    """
    Verifies a trace is well-formed and valid

    Parameters
    ----------
    xpad_idl_trace : numpy.core.records.recarray
        A trace from imported XPad *.padsav data


    Returns
    -------
    int : 0 for invalid, 1 for valid
    """
    from numpy import prod
    from numpy.core.records import recarray

    # [*] 'xpad_idl_trace is not an instance of numpy.core.records.recarray'
    if not isinstance(xpad_idl_trace, recarray):
        return 0

    # [*] 'UTYPE != \'DBstructure\''
    if (
        "UTYPE" not in xpad_idl_trace.dtype.names
        or not xpad_idl_trace["UTYPE"][0] == "DBstructure"
    ):
        return 0

    for field in [
        "TYPE",
        "NAME",
        "DATA",
        "DINFO",
        "SOURCE",
        "PROCESS",
        "SIZE",
        "TINFO",
    ]:
        # [*] 'Required field missing: '+field
        if field not in xpad_idl_trace.dtype.names:
            return 0

    # [*] TINFO.UTYPE != \'TINFO\'
    if (
        "UTYPE" not in xpad_idl_trace["TINFO"][0].dtype.names
        or not xpad_idl_trace["TINFO"][0]["UTYPE"][0] == "TINFO"
    ):
        return 0

    for field in [
        "DOMAINS",
        "START",
        "FINISH",
        "STEP",
        "SAMPLES",
        "LENGTH",
        "UNITS",
        "LABEL",
    ]:
        # [*] 'Required TINFO field missing: '+field
        if field not in xpad_idl_trace["TINFO"][0].dtype.names:
            return 0

    types = ["f(t)", "f(t,x)", "f(t,x,y)"]
    # [*] 'TYPE is not one of '+str(types)
    if not xpad_idl_trace["TYPE"][0] in types:
        return 0

    sizes = xpad_idl_trace["SIZE"][0]
    numdims = sizes[0]
    # [*] 'size(DATA) != prod(dim_sizes)'
    if not xpad_idl_trace["DATA"][0].size == prod(sizes[1:]):
        return 0

    # [*] 'Incorrect numdims for shape of DATA'
    if not numdims == len(xpad_idl_trace["DATA"][0].shape):
        return 0

    # [*] 'Incorrect numdims in SIZE for TYPE'
    if not numdims == types.index(xpad_idl_trace["TYPE"][0]) + 1:
        return 0

    if numdims > 0:
        if xpad_idl_trace["TINFO"][0]["DOMAINS"][0] < 1:
            if "TIME" in xpad_idl_trace.dtype.names:
                # [*] 'size(TIME) != SIZE[1]':
                if not xpad_idl_trace["TIME"][0].size == sizes[1]:
                    return 0

                # Should this always be true?
                # [*] 'size(TIME) != TINFO.LENGTH':
                # if not xpad_idl_trace['TIME'][0].size == xpad_idl_trace['TINFO'][0]['LENGTH'][0]: return 0
            else:
                # Can't determine TIME dimension
                # [*] 'TINFO contains no domains and TIME field does not exist'
                return 0
        else:
            # [*] 'TINFO.START > TINFO.FINISH'
            if (
                not xpad_idl_trace["TINFO"][0]["START"][0]
                <= xpad_idl_trace["TINFO"][0]["FINISH"][0]
            ):
                return 0

            # [*] 'TINFO.LENGTH is < 1'
            if not xpad_idl_trace["TINFO"][0]["LENGTH"][0] >= 1:
                return 0

    if numdims > 1:
        for field in ["X", "XINFO"]:
            # [*] 'Required field missing: '+field
            if field not in xpad_idl_trace.dtype.names:
                return 0

        # [*] 'size(X) != SIZE[2]':
        if not xpad_idl_trace["X"][0].size == sizes[2]:
            return 0

    if numdims > 2:
        for field in ["Y", "YINFO"]:
            # [*] 'Required field missing: '+field
            if field not in xpad_idl_trace.dtype.names:
                return 0

        # [*] 'size(Y) != SIZE[3]':
        if not xpad_idl_trace["Y"][0].size == sizes[3]:
            return 0

    # Add more checks if you so desire
    # ...
    return 1
