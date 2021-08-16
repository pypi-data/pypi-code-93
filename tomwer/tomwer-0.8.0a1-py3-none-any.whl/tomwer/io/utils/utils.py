# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""
contains utils for inputs and outputs
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "07/09/2020"


import numpy.lib.npyio
import os
from silx.io.utils import get_data as silx_get_data
from tomwer.core.utils import ftseriesutils
from PIL import Image
import logging

_logger = logging.getLogger(__name__)


def get_slice_data(url):
    """Return data from an url"""
    if os.path.exists(url.file_path()) and os.path.isfile(url.file_path()):
        if url.file_path().lower().endswith(
            ".vol.info"
        ) or url.file_path().lower().endswith(".vol"):
            data = _loadVol(url)
        elif url.scheme() == "numpy":
            data = numpy.load(url.file_path())
            if isinstance(data, numpy.lib.npyio.NpzFile):
                data = data["result"]
            data = data
        elif url.scheme() == "tomwer":
            data = numpy.array(Image.open(url.file_path()))
            if url.data_slice() is not None:
                data = data[url.data_slice()]
        else:
            try:
                data = silx_get_data(url)
            except Exception as e:
                _logger.error(e)
                _logger.warning("file %s not longer exists or is empty" % url)
                data = None
    else:
        _logger.warning("file %s not longer exists or is empty" % url)
        data = None
    return data


def _loadVol(url):
    """Load data from a .vol file and an url"""
    if url.file_path().lower().endswith(".vol.info"):
        infoFile = url.file_path()
        rawFile = url.file_path().replace(".vol.info", ".vol")
    else:
        assert url.file_path().lower().endswith(".vol")
        rawFile = url.file_path()
        infoFile = url.file_path().replace(".vol", ".vol.info")

    if not os.path.exists(rawFile):
        data = None
        mess = "Can't find raw data file %s associated with %s" % (rawFile, infoFile)
        _logger.warning(mess)
    elif not os.path.exists(infoFile):
        mess = "Can't find info file %s associated with %s" % (infoFile, rawFile)
        _logger.warning(mess)
        data = None
    else:
        shape = ftseriesutils.get_vol_file_shape(infoFile)
        if None in shape:
            _logger.warning("Fail to retrieve data shape for %s." % infoFile)
            data = None
        else:
            try:
                numpy.zeros(shape)
            except MemoryError:
                data = None
                _logger.warning(
                    "Raw file %s is to large for being " "readed %s" % rawFile
                )
            else:
                data = numpy.fromfile(rawFile, dtype=numpy.float32, count=-1, sep="")
                try:
                    data = data.reshape(shape)
                except ValueError:
                    _logger.warning(
                        "unable to fix shape for raw file %s. "
                        "Look for information in %s"
                        "" % (rawFile, infoFile)
                    )
                    try:
                        sqr = int(numpy.sqrt(len(data)))
                        shape = (1, sqr, sqr)
                        data = data.reshape(shape)
                    except ValueError:
                        _logger.info("deduction of shape size for %s failed" % rawFile)
                        data = None
                    else:
                        _logger.warning(
                            "try deducing shape size for %s "
                            "might be an incorrect "
                            "interpretation" % rawFile
                        )
    if url.data_slice() is None:
        return data
    else:
        return data[url.data_slice()]


def get_default_directory() -> str:
    """

    :return: default directory where to open a QFolder dialdg for example
    :rtype: str
    """
    if "TOMWER_DEFAULT_INPUT_DIR" in os.environ and os.path.exists(
        os.environ["TOMWER_DEFAULT_INPUT_DIR"]
    ):
        return os.environ["TOMWER_DEFAULT_INPUT_DIR"]
    else:
        return os.getcwd()


def format_stderr_stdout(stdout, stderr, config=None):
    s_out = stdout.decode("utf-8") if stdout is not None else ""
    s_err = stderr.decode("utf-8") if stderr is not None else ""
    if config is None:
        config = ""
    else:
        assert isinstance(config, dict)
    return (
        "############# nabu ############## \nconfig: {}\n"
        "------------- stderr -------------\n{}\n"
        "------------- stdout -------------\n{}\n".format(config, s_err, s_out)
    )
