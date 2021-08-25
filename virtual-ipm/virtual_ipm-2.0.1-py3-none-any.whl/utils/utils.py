#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import logging
import re

import numpy as np


def arrange_input_as(xmin, xmax, npoints, func='linear'):
    """
    Arranges data on a given interval according to a given function.

    Parameters
    ----------
    xmin : float
        Lower boundary of the interval.
    xmax : float
        Upper boundary of the interval
    npoints : int
        Number of points the interval should be divided into.
    func : unicode or tuple
        The following arrangements can be selected via string: ``'linear'`` and ``'log10'``.
        If given as a tuple it must contain exactly two callables, where the first represents
        the function and the second represents its inverse.

    Returns
    -------
    data : :class:`np.ndarray`, shape (npoints,)
        A numpy array containing `npoints` data points arranged according to
        the specified function.
    """

    if isinstance(func, str):
        if func == 'linear':
            func, inv_func = lambda x: x, lambda x: x
        elif func == 'log10':
            func, inv_func = np.log10, lambda x: 10 ** x
        else:
            raise ValueError('Unknown function: %s' % func)
    elif isinstance(func, tuple):
        if len(func) != 2:
            raise ValueError('func must be a tuple of function and inverse function')
        func, inv_func = func
    else:
        raise TypeError('`func` must be unicode or tuple (got %s instead)' % type(func))

    xmin, xmax = func(xmin), func(xmax)
    xstep = (xmax - xmin) / (npoints - 1)
    x = np.array([inv_func(xmin + i * xstep) for i in range(npoints)], dtype=float)

    return x


def convert_camel_case_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_logger(name):
    return logging.getLogger(name)


def log_entry_and_exit(entry_msg='Enter ...', exit_msg='... exit.', level=logging.DEBUG):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if entry_msg:
                self.logger.log(level, '[ %s ] %s' % (func.__name__, entry_msg))
            result = func(self, *args, **kwargs)
            if exit_msg:
                self.logger.log(level, '[ %s ] %s' % (func.__name__, exit_msg))
            return result
        return wrapper
    return decorator


def with_logger(module_name):
    def decorator(cls):
        cls.logger = get_logger('%s.%s' % (module_name, cls.__name__))
        return cls
    return decorator


def to_json_string(obj):
    return json.dumps(obj, indent=4)
