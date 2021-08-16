# coding: utf-8
# /*##########################################################################
# Copyright (C) 2017 European Synchrotron Radiation Facility
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
#############################################################################*/

"""
This module is used to define the process of the reference creator.
This is related to the issue #184
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "19/07/2018"

import fnmatch
import logging
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
import os
import re

from tomwer.core.process.baseprocess import SingleProcess, _input_desc, _output_desc

_logger = logging.getLogger(__name__)


class BaseFilter(object):
    """
    Apply a filter to an object
    """

    def description(self):
        pass

    def isFiltered(self, value):
        """
        Return True if the value not filtered

        """
        raise NotImplementedError("Base class")


class _PatternBaseFilter(BaseFilter):
    """Filter based on a pattern"""

    def __init__(self, pattern):
        BaseFilter.__init__(self)
        self.setPattern(pattern)

    def setPattern(self, pattern):
        """
        compile th filter for the given pattern
        :param str pattern:
        """
        self._pattern = pattern

    def getPattern(self):
        return self._pattern


class RegularExpressionFilter(_PatternBaseFilter):
    """Filter a string based on a defined pattern"""

    def __init__(self, pattern):
        _PatternBaseFilter.__init__(self, pattern=pattern)

    def setPattern(self, pattern):
        """
        compile th filter for the given pattern
        :param str pattern:
        """
        super().setPattern(pattern)
        if self._pattern is not None:
            try:
                self._filter = re.compile(self._pattern)
            except re.error as e:
                self.unvalidPatternDefinition(self._pattern, e)
                _logger.error(e)

    def description(self):
        return "Filter a string base on a regular expression"

    def isFiltered(self, value):
        try:
            match = self._filter.match(value) is None
        except:
            return False
        else:
            return match

    def unvalidPatternDefinition(self, pattern, error):
        _logger.error("%s is not a valid pattern. Error is %s" % (pattern, error))


class UnixFileNamePatternFilter(_PatternBaseFilter):
    """Filter a string based on 'fnmatch' module (unix filename pattern
    matching)"""

    def __init__(self, pattern):
        _PatternBaseFilter.__init__(self, pattern)

    def description(self):
        return "Filter a string base on a glob (unix style pathname)"

    def isFiltered(self, value):
        try:
            match = fnmatch.fnmatch(value, self._pattern)
        except:
            match = False
        return not match


class FileNameFilter(_PatternBaseFilter, SingleProcess):
    """Filter than can call several filter type"""

    inputs = [
        _input_desc(
            name="data", type=TomwerScanBase, handler="process", doc="scan path"
        )
    ]

    outputs = [_output_desc(name="data", type=TomwerScanBase, doc="scan path")]

    FILTER_TYPES = "unix file name pattern", "regular expression"

    _DEFAULT_FILTER_TYPE = FILTER_TYPES[0]

    def __init__(self, pattern):
        self._fnFilter = UnixFileNamePatternFilter(pattern)
        self._reFilter = RegularExpressionFilter(pattern)
        self._filters = {}
        self._filters["unix file name pattern"] = self._fnFilter
        self._filters["regular expression"] = self._reFilter
        self._activeFilter = self._DEFAULT_FILTER_TYPE

        _PatternBaseFilter.__init__(self, pattern)
        SingleProcess.__init__(self)
        self.activeFilter = self._DEFAULT_FILTER_TYPE

    @property
    def activeFilter(self):
        return self._activeFilter

    @activeFilter.setter
    def activeFilter(self, filter_type):
        assert filter_type in self.FILTER_TYPES
        self._activeFilter = filter_type
        self._filters[self.activeFilter].setPattern(pattern=self.getPattern())

    def setPattern(self, pattern):
        super().setPattern(pattern)
        self._filters[self._activeFilter].setPattern(pattern)

    def isFiltered(self, value):
        return self._filters[self._activeFilter].isFiltered(value)

    def process(self, scan):
        _scan = scan
        if isinstance(scan, dict):
            _scan = ScanFactory.create_scan_object_frm_dict(scan)
        if _scan is None:
            return False
        assert isinstance(_scan, TomwerScanBase)

        if not self.isFiltered(os.path.basename(_scan.path)):
            if self._return_dict:
                return _scan.to_dict()
            else:
                return _scan
        else:
            return
