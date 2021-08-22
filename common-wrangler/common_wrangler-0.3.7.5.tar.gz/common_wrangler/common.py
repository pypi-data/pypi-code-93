# coding=utf-8

"""
Common methods for this project and others in the "wrangler" series
"""

import argparse
import csv
import difflib
import errno
import fnmatch
import json
import math
import re
import shutil
from collections import OrderedDict
import numpy as np
import os
import six
import sys
import matplotlib.pyplot as plt
# from datetime import datetime
from collections.abc import Iterable
# from itertools import chain, islice
from shutil import copy2, Error, copystat
from contextlib import contextmanager
from matplotlib.ticker import AutoMinorLocator
from matplotlib.patches import Rectangle

# Constants #

TPL_IO_ERR_MSG = "Couldn't read template at: '{}'"
MISSING_SEC_HEADER_ERR_MSG = "Configuration files must start with a section header such as '[main]'. Check file: {}"
BACKUP_TS_FMT = "_%Y-%m-%d_%H-%M-%S_%f"

# Boltzmann's Constant in ...
BOLTZ_CONST = 0.0019872041  # kcal/mol Kelvin
KB = 1.380649e-23  # [J/K]

# Planck's Constant in ...
PLANCK_CONST_KCAL = 9.53707e-14  # kcal s / mol
PLANCK_CONST_JS = 6.62607015e-34  # [Js]

# Universal gas constant in ...
RG = 0.001985877534  # kcal/mol K
GAS_CONSTANT = 8.314462618  # J / K / mol

AVOGADRO_CONST = 6.02214076e23  # 1 / mol
EHPART_TO_KCAL_MOL = 627.5094709  # [kcal/mol/(Eh/part)]
AMU_TO_KG = 1.66053906660e-27  # UNIT CONVERSION
AU_TO_J = 4.184 * EHPART_TO_KCAL_MOL * 1000.0  # UNIT CONVERSION
KCAL_MOL_TO_J_PART = 4184 / AVOGADRO_CONST
SPEED_OF_LIGHT = 2.99792458e10  # cm / s
ATM_TO_KPA = 101.325  # 1 atm in kPa

XYZ_ORIGIN = np.zeros(3)

# for figures
DEF_FIG_WIDTH = 10
DEF_FIG_HEIGHT = 6
DEF_AXIS_SIZE = 20
DEF_TICK_SIZE = 15
DEF_FIG_DIR = './figs/'

COLORBREWER_BLUE = "#377eb8"
COLORBREWER_GREEN = "#4daf4a"
COLORBREWER_ORANGE = "#ff7f00"
COLORBREWER_PURPLE = "#984ea3"
COLORBREWER_RED = "#e41a1c"
COLORBREWER_LT_BLUE = "#a6cee3"
COLORBREWER_LT_GREEN = "#b2df8a"
COLORBREWER_LT_ORANGE = "#fdbf6f"
COLORBREWER_LT_PURPLE = "#cab2d6"
COLORBREWER_PINK = "#fb9a99"
COLORBREWER_LT_GRAY = "#999999"
COLOR_SEQUENCE = [COLORBREWER_BLUE, COLORBREWER_GREEN, COLORBREWER_ORANGE, COLORBREWER_PURPLE, COLORBREWER_RED,
                  COLORBREWER_LT_BLUE, COLORBREWER_LT_GREEN, COLORBREWER_LT_ORANGE, COLORBREWER_LT_PURPLE,
                  COLORBREWER_PINK, COLORBREWER_LT_GRAY]


COLORBREWER_BROWN = "#ff7f00"
COLORBREWER_YELLOW = "#ffff33"
# https://www.nrel.gov/comm-standards/web/typography.html https://thesource.nrel.gov/nrel-brand/
# converted pantone to hex with google
NREL_BLUE = "#007dcc"
NREL_LT_BLUE = "#00a6de"
NREL_GREEN = "#4f8c0d"
NREL_LT_GREEN = "#7dba00"
NREL_YELLOW = "#fcc917"
NREL_ORANGE = "#d48500"
NREL_GRAY = "#636b70"
NREL_LT_GRAY = "#c9c9c4"

NON_NUMERIC = csv.QUOTE_NONNUMERIC


# Tolerance initially based on double standard machine precision of 5 × 10−16 for float64 (decimal64)
# found to be too stringent
TOL = 1.e-8
# similarly, use this to round away the insignificant digits!
SIG_DECIMALS = 12

# For converting atomic number to species
ATOM_NUM_DICT = {1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
                 11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar',
                 19: 'K', 20: 'Ca', 21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni',
                 29: 'Cu', 30: 'Zn', 31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr',
                 37: 'Rb', 38: 'Sr', 39: 'Y​', 40: 'Zr', 41: 'Nb​', 42: 'Mo​', 43: 'Tc​', 44: 'Ru​', 45: 'Rh​',
                 46: 'Pd​', 47: 'Ag​', 48: 'Cd​', 49: 'In​', 50: 'Sn​', 51: 'Sb​', 52: 'Te​', 53: 'I​', 54: 'Xe',
                 74: 'W', 79: 'Au',
                 }

COMP = 'Isotopic Composition'
MASS = 'Standard Atomic Weight'
CARBON = 'C'
HYDROGEN = 'H'
OXYGEN = 'O'
NITROGEN = 'N'
SULFUR = 'S'
FLORINE = 'F'
CHLORINE = 'Cl'
BROMINE = 'Br'
IODINE = 'I'
SODIUM = 'Na'
POTASSIUM = 'K'
GERMANIUM = 'Ge'
SILICON = 'Si'
# from NIST, 2020
ISOTOPE_MASS_DICT = {HYDROGEN: {COMP: [0.9998857, 0.0001157], MASS: [1.007825032, 2.014101778]},
                     CARBON: {COMP: [0.9893800, 0.0107800], MASS: [12.00000000, 13.00335484]},
                     NITROGEN: {COMP: [0.9963620, 0.0036420], MASS: [14.0030740044320, 15.0001088988864]},
                     OXYGEN: {COMP: [0.9975716, 0.000381, 0.0020514], MASS: [15.99491462, 16.99913176, 17.99915961]},
                     FLORINE: {COMP: [1.0], MASS: [18.99840316]},
                     SODIUM: {COMP: [1.0], MASS: [22.98976928]},
                     SULFUR: {COMP: [0.949926, 0.00752, 0.042524, 0.00011],
                              MASS: [31.97207117, 32.97145891, 33.967867, 35.96708071]},
                     CHLORINE: {COMP: [0.75761, 0.24241], MASS: [34.96885268, 36.9659026]},
                     POTASSIUM: {COMP: [0.93258144, 0.0001171, 0.06730244],
                                 MASS: [38.96370649, 39.96399817, 40.96182526]},
                     BROMINE: {COMP: [0.50697, 0.49317], MASS: [78.91833761, 80.91628971]},
                     GERMANIUM: {COMP: [0.205727, 0.274532, 0.077512, 0.36502, 0.077312],
                                 MASS: [69.92424876, 71.92207583, 72.92345896, 73.92117776, 75.92140273]},
                     SILICON: {COMP: [0.9222319, 0.046858, 0.0309211], MASS: [27.97692653, 28.97649466, 29.97377014]}
                     }

# Common config variables
OUT_DIR = 'out_dir'

# Sections for reading files
MAIN_SEC = 'main'
SEC_TIMESTEP = 'timestep'
SEC_NUM_ATOMS = 'dump_num_atoms'
SEC_BOX_SIZE = 'dump_box_size'
SEC_ATOMS = 'atoms_section'
SEC_HEAD = 'head_section'
SEC_TAIL = 'tail_section'
ATOM_TYPE = 'atom_type'
ATOM_COORDS = 'atom_coords'

# From template files
BASE_NAME = 'base_name'
NUM_ATOMS = 'num_atoms'
HEAD_CONTENT = 'head_content'
ATOMS_CONTENT = 'atoms_content'
TAIL_CONTENT = 'tail_content'

# Lammps-specific sections
MASSES = 'Masses'
PAIR_COEFFS = 'Pair Coeffs'
ATOMS = 'Atoms'
BOND_COEFFS = 'Bond Coeffs'
BONDS = 'Bonds'
ANGLE_COEFFS = 'Angle Coeffs'
ANGLES = 'Angles'
DIHE_COEFFS = 'Dihedral Coeffs'
DIHES = 'Dihedrals'
IMPR_COEFFS = 'Improper Coeffs'
IMPRS = 'Impropers'
LAMMPS_SECTION_NAMES = [MASSES, PAIR_COEFFS, ATOMS, BOND_COEFFS, BONDS, ANGLE_COEFFS, ANGLES,
                        DIHE_COEFFS, DIHES, IMPR_COEFFS, IMPRS]

# PDB file info
PDB_FORMAT = '{:s}{:s}{:s}{:s}{:4d}    {:8.3f}{:8.3f}{:8.3f}{:s}'
PDB_LINE_TYPE_LAST_CHAR = 6
PDB_ATOM_NUM_LAST_CHAR = 11
PDB_ATOM_TYPE_LAST_CHAR = 17
PDB_RES_TYPE_LAST_CHAR = 22
PDB_MOL_NUM_LAST_CHAR = 28
PDB_X_LAST_CHAR = 38
PDB_Y_LAST_CHAR = 46
PDB_Z_LAST_CHAR = 54
PDB_BEFORE_ELE_LAST_CHAR = 76
PDB_ELE_LAST_CHAR = 78


# Error Codes
# The good status code
GOOD_RET = 0
INPUT_ERROR = 1
IO_ERROR = 2
INVALID_DATA = 3


# Exceptions #

class CommonError(Exception):
    pass


class InvalidInputError(CommonError):
    pass


class InvalidDataError(CommonError):
    pass


class NotFoundError(CommonError):
    pass


class ArgumentParserError(Exception):
    pass


class TemplateNotReadableError(Exception):
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)


def warning(*objs):
    """Writes a message to stderr."""
    print("WARNING: ", *objs, file=sys.stderr)


# Test utilities


# From http://schinckel.net/2013/04/15/capture-and-test-sys.stdout-sys.stderr-in-unittest.testcase/
@contextmanager
def capture_stdout(command, *args, **kwargs):
    # pycharm doesn't know six very well, so ignore the false warning
    # noinspection PyCallingNonCallable
    out, sys.stdout = sys.stdout, six.StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


@contextmanager
def capture_stderr(command, *args, **kwargs):
    # pycharm doesn't know six very well, so ignore the false warning
    # noinspection PyCallingNonCallable
    err, sys.stderr = sys.stderr, six.StringIO()
    command(*args, **kwargs)
    sys.stderr.seek(0)
    yield sys.stderr.read()
    sys.stderr = err


# Calculations #


# def calc_kbt(temp_k):
#     """
#     Returns the given temperature in Kelvin multiplied by Boltzmann's Constant.
#
#     :param temp_k: A temperature in Kelvin.
#     :return: The given temperature in Kelvin multiplied by Boltzmann's Constant.
#     """
#     return BOLTZ_CONST * temp_k
#

def calc_k(temp, delta_gibbs):
    """
    Returns the rate coefficient calculated from Transition State Theory in inverse seconds
    :param temp: the temperature in Kelvin
    :param delta_gibbs: the change in Gibbs free energy in kcal/mol
    :return: rate coefficient in inverse seconds
    """
    return BOLTZ_CONST * temp / PLANCK_CONST_KCAL * math.exp(-delta_gibbs / (RG * temp))


def calc_dist(a, b):
    return np.linalg.norm(np.subtract(a, b))


# # TODO: add test?
# #   maybe move to md_common: pbc_dist, first_pbc_image
# def pbc_dist(a, b, box):
#     # TODO: make a test that ensures the distance calculated is <= sqrt(sqrt((a/2)^2+(b/2)^2) + (c/2)^2)) ?
#     return np.linalg.norm(pbc_calc_vector(a, b, box))
#

def pbc_calc_vector(a, b, box):
    """
    Finds the vectors between two points
    :param a: xyz coords 1
    :param b: xyz coords 2
    :param box: vector with PBC box dimensions
    :return: returns the vector a - b
    """
    vec = np.subtract(a, b)
    return vec - np.multiply(box, np.asarray(list(map(round, vec / box))))


# def first_pbc_image(xyz_coords, box):
#     """
#     Moves xyz coords to the first PBC image, centered at the origin
#     :param xyz_coords: coordinates to center (move to first image)
#     :param box: PBC box dimensions
#     :return: xyz coords (np array) moved to the first image
#     """
#     return pbc_calc_vector(xyz_coords, XYZ_ORIGIN, box)


def pbc_vector_avg(a, b, box):
    diff = pbc_calc_vector(a, b, box)
    mid_pt = np.add(b, np.divide(diff, 2.0))
    # mid-point may not be in the first periodic image. Make it so by getting its difference from the origin
    return pbc_calc_vector(mid_pt, np.zeros(len(mid_pt)), box)


def unit_vector(vector):
    """ Returns the unit vector of the vector.
    http://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
    """
    return vector / np.linalg.norm(vector)


def vec_angle(vec_1, vec_2):
    """
    Calculates the angle between the vectors (p2 - p1) and (p0 - p1)
    Note: assumes the vector calculation accounted for the PBC
    :param vec_1: xyz coordinate for the first pt
    :param vec_2: xyz for 2nd pt
    :return: the angle in between the vectors
    """
    unit_vec_1 = unit_vector(vec_1)
    unit_vec_2 = unit_vector(vec_2)

    return np.rad2deg(np.arccos(np.clip(np.dot(unit_vec_1, unit_vec_2), -1.0, 1.0)))


def vec_dihedral(vec_ba, vec_bc, vec_cd):
    """
    calculates the dihedral angle from the vectors b --> a, b --> c, c --> d
    where a, b, c, and d are the four points
    From:
    http://stackoverflow.com/questions/20305272/
      dihedral-torsion-angle-from-four-points-in-cartesian-coordinates-in-python
    Khouli formula
    1 sqrt, 1 cross product
    :param vec_ba: the vector connecting points b --> a, accounting for pbc
    :param vec_bc: b --> c
    :param vec_cd: c --> d
    :return: dihedral angle in degrees
    """
    # normalize b1 so that it does not influence magnitude of vector
    # rejections that come next
    vec_bc = unit_vector(vec_bc)

    # vector rejections
    # v = projection of b0 onto plane perpendicular to b1
    #   = b0 minus component that aligns with b1
    # w = projection of b2 onto plane perpendicular to b1
    #   = b2 minus component that aligns with b1
    v = vec_ba - np.dot(vec_ba, vec_bc) * vec_bc
    w = vec_cd - np.dot(vec_cd, vec_bc) * vec_bc

    # angle between v and w in a plane is the torsion angle
    # v and w may not be normalized but that's fine since tan is y/x
    x = np.dot(v, w)
    y = np.dot(np.cross(vec_bc, v), w)
    return np.degrees(np.arctan2(y, x))


# Other #

# # TODO: find if ever used, and if so, test
# def chunk(seq, chunk_size, process=iter):
#     """Yields items from an iterator in iterable chunks.
#     From https://gist.github.com/ksamuel/1275417
#
#     :param seq: The sequence to chunk.
#     :param chunk_size: The size of the returned chunks.
#     :param process: The function to use for creating the iterator.  Useful for iterating over different
#     data structures.
#     :return: Chunks of the given size from the given sequence.
#     """
#     it = iter(seq)
#     while True:
#         yield process(chain([six.next(it)], islice(it, chunk_size - 1)))


# I/O #

def read_tpl(tpl_loc):
    """Attempts to read the given template location and throws A
    TemplateNotReadableError if it can't read the given location.

    :param tpl_loc: The template location to read.
    :raise TemplateNotReadableError: If there is an IOError reading the location.
    """
    try:
        return file_to_str(tpl_loc)
    except IOError:
        raise TemplateNotReadableError(TPL_IO_ERR_MSG.format(tpl_loc))


def make_dir(tgt_dir):
    """
    Creates the given directory and its parent directories if it
    does not already exist.

    Keyword arguments:
    tgt_dir -- The directory to create

    """
    if not os.path.exists(tgt_dir):
        os.makedirs(tgt_dir)
    elif not os.path.isdir(tgt_dir):
        raise NotFoundError("Resource exists and is not a dir: {}".format(tgt_dir))


def overwrite_config_vals(args, arg_config_keyword_dict, default_val_dict):
    """
    Method to overwrite args.config[KEY] values with args.key values, as long as the args.key values are different
    than the default values.
    :param args: argparse namespace
    :param arg_config_keyword_dict: dictionary of args.key (keys) with corresponding args.config[KEY] (values)
    :param default_val_dict: dict with default args.config[KEY] values
    :return: n/a, updates args.config
    """
    arg_dict = vars(args)
    # any provided value that is not default will overwrite a config value that is default or read from a cfg ini
    for arg_key, config_key in arg_config_keyword_dict.items():
        arg_val = arg_dict[arg_key]
        def_val = default_val_dict[config_key]
        if isinstance(arg_val, float) or isinstance(def_val, float):
            if not np.isclose(arg_val, def_val):
                args.config[config_key] = arg_val
        else:
            if arg_val != def_val:
                args.config[config_key] = arg_val


def file_to_str(f_name):
    """
    Reads and returns the contents of the given file.

    :param f_name: The location of the file to read.
    :return: The contents of the given file.
    :raises: IOError if the file can't be opened for reading.
    """
    with open(f_name) as f:
        return f.read()


def file_rows_to_list(c_file):
    """
    Given the name of a file, returns a list of its rows, after filtering out empty rows
    :param c_file: file location
    :return: list of non-empty rows
    """
    with open(c_file) as f:
        row_list = [row.strip() for row in f.readlines()]
        return list(filter(None, row_list))


def str_to_file(str_val, f_name, mode='w', print_info=False):
    """
    Writes the string to the given file.
    :param str_val: The string to write.
    :param f_name: The location of the file to write
    :param mode: default mode is to overwrite file
    :param print_info: boolean to specify whether to print action to stdout
    """
    with open(f_name, mode) as f:
        f.write(str_val)
    if print_info:
        rel_path_name = os.path.relpath(f_name)
        if mode == 'a':
            print(f"  Appended: {rel_path_name}")
        else:
            print(f"Wrote file: {rel_path_name}")


def round_to_12th_decimal(val):
    """
    To remove floating point digits that are imprecise due to expected machine precision
    :param val: a float
    :return: a float without insignificant digits
    """
    return round(val, SIG_DECIMALS)


def round_sig_figs(num, sig_figs=6):
    """
    Rounds a given float to the specified number of significant figures. It uses the uses a built-in function through
    formatting, since built-in functions are generally faster.
    :param num: float or int
    :param sig_figs: number of significant figures to return
    :return: float or int (same as given)
    """
    # start by making a float even if started as an integer, as the number may be first converted to scientific
    #    notation, which cannot be directly converted to an int
    #    scientific notation
    # Didn't see a clean way to do in python 2.7, so ignoring incompatibility
    # noinspection PyCompatibility
    str_num = f'{num:.{sig_figs}g}'
    if isinstance(num, int):
        intermediate_val = float(str_num)
        return int(intermediate_val)
    elif isinstance(num, np.float64):
        return np.float64(str_num)
    elif isinstance(num, np.float32):
        return np.float32(str_num)
    else:
        return float(str_num)


def round_to_fraction(array, increment):
    """
    Numpy around, trunc, ceil, floor, ... can round numbers based on base 10 (e.g. 0.01).
    The method can round to any fraction of 1
    FYI: only tested on positive numbers. Check behavior for negative numbers if needed.
    :param array: array_like input data
    :param increment: float, the fraction of 1 that should be used for rounding
    :return: array, rounded to closest increment
    """
    try:
        # only one integer is allowable: 1
        if not (isinstance(increment, float) or increment == 1):
            raise InvalidDataError
        if increment < 0:
            raise InvalidDataError
        tolerance = 1e-6
        base_10_log = -np.log10(increment)
        if base_10_log < 0:
            raise InvalidDataError
        diff = abs(base_10_log - round(base_10_log, 0))
        if diff < tolerance:
            return np.around(array, int(base_10_log))
        remainder = 1. % increment
        # sometimes the remainder is almost the increment--check for that, too
        if remainder > tolerance and (increment - remainder) > tolerance:
            raise InvalidDataError
        whole_number = round(1. / increment, 0)
        return np.around(np.multiply(array, whole_number)) / whole_number
    except InvalidDataError:
        raise InvalidDataError("This function expects a positive number that evenly divides into 1 (that is, 1 is a "
                               "multiple of the provided number), which is not the case for the provided increment "
                               "of {}".format(increment))


def a_to_i(text):
    """
    Converts a string to an int if possible
    :param text: str to possibly be converted
    :return: either int (if text could be converted) or the same str back
    """
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    Helper script for sorting with "natural keys" (e.g. sorts numbers as full numbers, so 222 does not come before 4)

    from https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
    a_list.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html

    :param text: str, part of a list to be sorted using "natural keys"
    :return: the text split into a list of alternating strings and ints to help with sorting
    """
    return [a_to_i(c) for c in re.split(r'(\d+)', text)]


def read_json(fname):
    try:
        with open(fname) as json_file:
            return json.load(json_file)
    except json.decoder.JSONDecodeError:
        raise InvalidDataError(f"Error in reading JSON format for file: {fname}")


def save_json(data, fname, print_message=True):
    with open(fname, 'w') as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)
    if print_message:
        print(f"Wrote file: {os.path.relpath(fname)}")


# TODO: continue adding tests here
def np_float_array_from_file(data_file, delimiter=" ", header=False, gather_hist=False):
    """
    Adds to the basic np.loadtxt by performing data checks.
    :param data_file: file expected to have space-separated values, with the same number of entries per row
    :param delimiter: default is a space-separated file
    :param header: default is no header; alternately, specify number of header lines
    :param gather_hist: default is false; gather data to make histogram of non-numerical data
    :return: a numpy array or InvalidDataError if unsuccessful, followed by the header_row (None if none specified)
    """
    header_row = None
    hist_data = {}
    with open(data_file) as csv_file:
        csv_list = list(csv.reader(csv_file, delimiter=delimiter))
    if header:
        header_row = csv_list[0]

    try:
        data_array = np.genfromtxt(data_file, dtype=np.float64, delimiter=delimiter, skip_header=header)
    except ValueError:
        data_array = None
        line_len = None
        if header:
            if isinstance(header, int):
                first_line = header
            else:
                first_line = 1
        else:
            first_line = 0
        for row in csv_list[first_line:]:
            if len(row) == 0:
                continue
            s_len = len(row)
            if line_len is None:
                line_len = s_len
            elif s_len != line_len:
                raise InvalidDataError('File could not be read as an array of floats: {}\n  Expected '
                                       'values separated by "{}" with an equal number of columns per row.\n'
                                       '  However, found {} values on the first data row'
                                       '  and {} values on the later row: "{}")'
                                       ''.format(data_file, delimiter, line_len, s_len, row))
            data_vector = np.empty([line_len], dtype=np.float64)
            for col in range(line_len):
                try:
                    data_vector[col] = float(row[col])
                except ValueError:
                    data_vector[col] = np.nan
                    if gather_hist:
                        col_key = str(row[col])
                        if col in hist_data:
                            if col_key in hist_data[col]:
                                hist_data[col][col_key] += 1
                            else:
                                hist_data[col][col_key] = 1
                        else:
                            hist_data[col] = {col_key: 1}
            if data_array is None:
                data_array = np.copy(data_vector)
            else:
                data_array = np.vstack((data_array, data_vector))
    if len(data_array.shape) == 1:
        raise InvalidDataError("File contains a vector, not an array of floats: {}\n".format(data_file))
    if np.isnan(data_array).any():
        warning("Encountered entry (or entries) which could not be converted to a float. "
                "'nan' will be returned for those entries.")
        if not header:
            warning("Check if first line is a header, as no header is specified.")
    if len(hist_data) > 0 or header_row:
        if len(hist_data) > 0 and header_row:
            return data_array, header_row, hist_data
        elif header_row:
            return data_array, header_row
        else:
            return data_array, hist_data
    else:
        return data_array


def read_csv_to_list(data_file, delimiter=',', header=False):
    """
    Reads file of values; did not use np.loadtxt because can have floats and strings
    :param data_file: name of delimiter-separated file with the same number of entries per row
    :param delimiter: string: delimiter between column values
    :param header: boolean to denote if file contains a header
    :return: a list containing the data (removing header row, if one is specified) and a list containing the
             header row (empty if no header row specified)
    """
    with open(data_file) as csv_file:
        csv_list = list(csv.reader(csv_file, delimiter=delimiter, quoting=csv.QUOTE_NONNUMERIC))

    header_row = []

    if header:
        first_line = 1
        header_row = csv_list[0]
    else:
        first_line = 0

    return csv_list[first_line:], header_row


# def create_backup_filename(orig):
#     base, ext = os.path.splitext(orig)
#     now = datetime.now()
#     return "".join((base, now.strftime(BACKUP_TS_FMT), ext))
#
#
# def find_backup_filenames(orig):
#     base, ext = os.path.splitext(orig)
#     found = glob.glob(base + "*" + ext)
#     try:
#         found.remove(orig)
#     except ValueError:
#         # Original not present; ignore.
#         pass
#     return found


def silent_remove(filename, disable=False, dir_with_files=False):
    """
    Removes the target file name, catching and ignoring errors that indicate that the
    file does not exist.

    :param filename: The file to remove.
    :param disable: boolean to flag if want to disable removal
    :param dir_with_files: boolean to delete files in dir also
    """
    if not disable:
        try:
            if os.path.isdir(filename):
                if dir_with_files:
                    shutil.rmtree(filename)
                else:
                    os.rmdir(filename)
            else:
                os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise


def allow_write(f_loc, overwrite=False):
    """
    Returns whether to allow writing to the given location.

    :param f_loc: The location to check.
    :param overwrite: Whether to allow overwriting an existing location.
    :return: Whether to allow writing to the given location.
    """
    if os.path.exists(f_loc) and not overwrite:
        warning("Not overwriting existing file '{}'".format(f_loc))
        return False
    return True


# def move_existing_file(f_loc):
#     """
#     Renames an existing file using a timestamp based on the move time.
#
#     :param f_loc: The location to check.
#     """
#     if os.path.exists(f_loc):
#         shutil.move(f_loc, create_backup_filename(f_loc))
#

def get_fname_root(src_file):
    """

    :param src_file:
    :return: the file root name (no directory, no extension)
    """
    return os.path.splitext(os.path.basename(src_file))[0]


def create_out_fname(src_file, prefix='', suffix='', remove_prefix=None, base_dir=None, ext=None, rel_path=False):
    """Creates an outfile name for the given source file.

    :param remove_prefix: string to remove at the beginning of file name
    :param src_file: The file to process.
    :param prefix: The file prefix to add, if specified.
    :param suffix: The file suffix to append, if specified.
    :param base_dir: The base directory to use; defaults to `src_file`'s directory.
    :param ext: The extension to use instead of the source file's extension;
        defaults to the `scr_file`'s extension.
    :param rel_path: boolean to indicate that the relative path, rather than the absolute path, is returned
    :return: The output file name.
    """

    if base_dir is None:
        base_dir = os.path.dirname(src_file)

    base_name = get_fname_root(src_file)

    if remove_prefix is not None and base_name.startswith(remove_prefix):
        base_name = base_name[len(remove_prefix):]

    if ext is None:
        ext = os.path.splitext(src_file)[1]

    if not ext.startswith("."):
        ext = "." + ext

    new_path = os.path.join(base_dir, prefix + base_name + suffix + ext)
    if rel_path:
        return os.path.relpath(new_path)
    else:
        return os.path.abspath(new_path)


def find_files_by_dir(tgt_dir, pat):
    """Recursively searches the target directory tree for files matching the given pattern.
    The results are returned as a dict with a list of found files keyed by the absolute
    directory name.
    :param tgt_dir: The target base directory.
    :param pat: The file pattern to search for.
    :return: A dict where absolute directory names are keys for lists of found file names
        that match the given pattern.
    """
    match_dirs = {}
    for root, dirs, files in os.walk(tgt_dir):
        matches = [match for match in files if fnmatch.fnmatch(match, pat)]
        if matches:
            match_dirs[os.path.abspath(root)] = matches
    return match_dirs


def check_for_files(file_name, file_list_name, search_pattern=None, search_dir=None, search_sub_dir=False,
                    warn_if_no_matches=True):
    """
    Checks that the file and/or list of files contains valid file names.
    :param file_name: None or str (file_name)
    :param file_list_name: None, str, or iterable (a file with a list of file names (one per line))
    :param search_pattern: str, used if searching directories
    :param search_dir: None (then searches current directory only, if no other choices are selected) or dir rel path
    :param search_sub_dir: Boolean, if True, search not just given search_dir (current if None) but also subdirs
    :param warn_if_no_matches: Boolean, if True, will raise an InvalidDataError if no files are found
    :return: a list of valid file names
    """
    # use a set to avoid duplicates, but will return a list
    valid_fnames = set()
    invalid_fnames = set()
    file_list = []
    if file_list_name is not None:
        if isinstance(file_list_name, list):
            file_list = file_list_name
        elif os.path.isfile(file_list_name):
            file_list = file_rows_to_list(file_list_name)
        else:
            raise InvalidDataError(f"Expected file name or list but encountered '{file_list_name}'")
    if file_name is not None:
        file_list.append(file_name)

    for fname in file_list:
        if os.path.isfile(fname):
            valid_fnames.add(os.path.relpath(fname))
        else:
            invalid_fnames.add(fname)

    # Will only find valid names in searching directories, so raise invalid fnames now
    if len(invalid_fnames) > 0:
        warning_message = "The following file name(s) could not be found:"
        for fname in invalid_fnames:
            warning_message += "\n    {}".format(fname)
        raise IOError(warning_message)

    # Only search directories if there is a pattern to match
    if search_pattern is not None:
        # convert to what regex will understand
        if not ("*" in search_pattern):
            mod_search_pattern = "*{}*".format(search_pattern)
        else:
            mod_search_pattern = search_pattern
        # change search_dir 'None' to current directory, if: search subdirectory specified, or neither file_name or
        #     file_list_name is specified (then defaults to check current subdirectory only)
        if search_dir is None and (search_sub_dir or (file_name is None and file_list_name is None)):
            search_dir = os.getcwd()
        if search_dir:
            if not os.path.isdir(search_dir):
                raise InvalidDataError("Could not find the specified directory '{}'".format(search_dir))
            if search_sub_dir:
                found_file_dict = find_files_by_dir(search_dir, mod_search_pattern)
                for found_dir, file_names in found_file_dict.items():
                    for fname in file_names:
                        valid_fnames.add(os.path.relpath(os.path.join(found_dir, fname)))
            else:
                valid_fnames.update([os.path.relpath(os.path.join(search_dir, match)) for match in
                                     os.listdir(search_dir) if fnmatch.fnmatch(match, mod_search_pattern)])

    if len(valid_fnames) == 0 and warn_if_no_matches:
        # additional note if did a dir search
        if search_dir:
            rel_search_dir = os.path.relpath(search_dir)
            warning_str = "Could not find files with pattern '{}' in directory '{}'".format(search_pattern,
                                                                                            rel_search_dir)
            if search_sub_dir:
                warning_str += " or its subdirectories."
            else:
                warning_str += "."
            warning(warning_str)
        raise InvalidDataError("No files to process.")

    # returns a sorted list, for predictability
    return sorted(valid_fnames)


def copytree(src, dst, symlinks=False, ignore=None):
    """This is a copy of the standard Python shutil.copytree, but it
    allows for an existing destination directory.

    Recursively copy a directory tree using copy2().

    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    :param src: The source directory.
    :param dst: The destination directory.
    :param symlinks: Whether to follow symbolic links.
    :param ignore: A callable for items to ignore at a given level.
    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.exists(dst):
        os.makedirs(dst)

    errors = []
    for name in names:
        if name in ignored_names:
            continue
        src_name = os.path.join(src, name)
        dst_name = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(src_name):
                link_to = os.readlink(src_name)
                os.symlink(link_to, dst_name)
            elif os.path.isdir(src_name):
                copytree(src_name, dst_name, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(src_name, dst_name)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((src_name, dst_name, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        # can't copy file access times on Windows
        # noinspection PyUnresolvedReferences
        if why.winerror is None:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)


# CSV #

def read_csv_header(src_file, return_second_row=False):
    """Returns a list containing the values from the first row (or second row) of the given CSV
    file or None if the file is empty.

    :param src_file: The CSV file to read.
    :param return_second_row: boolean to return 2nd row instead
    :return: The first row or None if empty.
    """
    with open(src_file) as csv_file:
        for row in csv.reader(csv_file):
            if return_second_row:
                return_second_row = False
                continue
            return list(row)


def convert_dict_line(all_conv, data_conv, line):
    s_dict = {}
    for s_key, s_val in line.items():
        if data_conv and s_key in data_conv:
            try:
                s_dict[s_key] = data_conv[s_key](s_val)
            except ValueError as e:
                warning("Could not convert value '{}' from column '{}': '{}'.  Leaving as str".format(s_val, s_key, e))
                s_dict[s_key] = s_val
        elif all_conv:
            try:
                s_dict[s_key] = all_conv(s_val)
            except ValueError as e:
                warning("Could not convert value '{}' from column '{}': '{}'.  Leaving as str".format(s_val, s_key, e))
                s_dict[s_key] = s_val
        else:
            s_dict[s_key] = s_val
    return s_dict


def read_csv(src_file, data_conv=None, all_conv=None, quote_style=csv.QUOTE_MINIMAL):
    """
    Reads the given CSV (comma-separated with a first-line header row) and returns a list of
    dicts where each dict contains a row's data keyed by the header row.

    :param src_file: The CSV to read.
    :param data_conv: A map of header keys to conversion functions.  Note that values
        that throw a TypeError from an attempted conversion are left as strings in the result.
    :param all_conv: A function to apply to all values in the CSV.  A specified data_conv value
        takes precedence.
    :param quote_style: how to read the dictionary
    :return: A list of dicts containing the file's data.
    """
    result = []
    with open(src_file) as csv_file:
        csv_reader = csv.DictReader(csv_file, quoting=quote_style)
        for line in csv_reader:
            result.append(convert_dict_line(all_conv, data_conv, line))
    return result


def read_csv_to_dict(src_file, col_name, data_conv=None, all_conv=None):
    """
    Reads the given CSV (comma-separated with a first-line header row) and returns a
    dict of dicts indexed on the given col_name. Each dict contains a row's data keyed by the header row.

    :param src_file: The CSV to read.
    :param col_name: the name of the column to index on
    :param data_conv: A map of header keys to conversion functions.  Note that values
        that throw a TypeError from an attempted conversion are left as strings in the result.
    :param all_conv: A function to apply to all values in the CSV.  A specified data_conv value
        takes precedence.
    :return: A list of dicts containing the file's data.
    """
    result = {}
    with open(src_file) as csv_file:
        try:
            csv_reader = csv.DictReader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            create_dict(all_conv, col_name, csv_reader, data_conv, result, src_file)
        except ValueError:
            csv_reader = csv.DictReader(csv_file)
            create_dict(all_conv, col_name, csv_reader, data_conv, result, src_file)
    return result


def create_dict(all_conv, col_name, csv_reader, data_conv, result, src_file):
    for line in csv_reader:
        val = convert_dict_line(all_conv, data_conv, line)
        if col_name in val:
            try:
                col_val = int(val[col_name])
            except ValueError:
                col_val = val[col_name]
            if col_val in result:
                warning("Duplicate values found for {}. Value for key will be overwritten.".format(col_val))
            result[col_val] = convert_dict_line(all_conv, data_conv, line)
        else:
            raise InvalidDataError("Could not find value for {} in file {} on line {}."
                                   "".format(col_name, src_file, line))


def write_csv(data, out_fname, fieldnames, extrasaction="raise", mode='w', quote_style=csv.QUOTE_NONNUMERIC,
              print_message=True, round_digits=False):
    """
    Given a list of dicts and fieldnames, writes a csv

    :param round_digits: if desired, provide decimal number for rounding
    :param data: The data to write (list of dicts).
    :param out_fname: The name of the file to write to.
    :param fieldnames: The sequence of field names to use for the header.
    :param extrasaction: What to do when there are extra keys.  Acceptable
        values are "raise" or "ignore".
    :param mode: default mode is to overwrite file
    :param print_message: boolean to flag whether to note that file written or appended
    :param quote_style: dictates csv output style
    """
    rel_out_name = os.path.relpath(out_fname)
    with open(out_fname, mode) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames, extrasaction=extrasaction, quoting=quote_style)
        execute_csv_dict_writer(data, mode, round_digits, writer)
    if print_message:
        if mode == 'a':
            print("  Appended: {}".format(rel_out_name))
        elif mode == 'w':
            print("Wrote file: {}".format(rel_out_name))


def print_csv_stdout(data, fieldnames, extrasaction="raise", mode="w",
                     quote_style=csv.QUOTE_NONNUMERIC, round_digits=False):
    """
    Given a list of dicts and fieldnames, writes a csv to stdout

    :param round_digits: if desired, provide decimal number for rounding
    :param data: The data to write (list of dicts).
    :param fieldnames: The sequence of field names to use for the header.
    :param extrasaction: What to do when there are extra keys.  Acceptable
        values are "raise" or "ignore".
    :param mode: default mode is to overwrite file
    :param quote_style: dictates csv output style
    """
    writer = csv.DictWriter(sys.stdout, fieldnames, extrasaction=extrasaction, quoting=quote_style)
    execute_csv_dict_writer(data, mode, round_digits, writer)


def execute_csv_dict_writer(data, mode, round_digits, writer):
    """
    Common method for csv.DictWriter to file or stdout

    :param writer: a csv.DictWriter object
    :param data: The data to write (list of dicts).
    :param round_digits: if desired, provide decimal number for rounding
    :param mode: if mode is "w", writes header
    """
    if mode == 'w':
        writer.writeheader()
    if round_digits:
        for row_id in range(len(data)):
            new_dict = {}
            for key, val in data[row_id].items():
                if isinstance(val, float):
                    new_dict[key] = round(val, round_digits)
                else:
                    new_dict[key] = val
            data[row_id] = new_dict
    writer.writerows(data)


def list_to_csv(data, out_fname, delimiter=',', mode='w', quote_style=csv.QUOTE_NONNUMERIC,
                print_message=True, round_digits=False):
    """
    Writes the given data to the given file location.
    :param data: The data to write (list of lists).
    :param out_fname: The name of the file to write to.
    :param delimiter: string
    :param mode: default mode is to overwrite file
    :param quote_style: csv quoting style
    :param print_message: boolean to allow update
    :param round_digits: boolean to affect printing output; supply an integer to round to that number of decimals
    """
    try:
        if not isinstance(data[0], list):
            data = [data]

        with open(out_fname, mode) as csv_file:
            writer = csv.writer(csv_file, delimiter=delimiter, quoting=quote_style)
            # TODO: see if can replace the "round_digits" if with the execute, but need to write test first
            # execute_csv_dict_writer(data, 'n', round_digits, writer)
            if round_digits:
                for row_id in range(len(data)):
                    new_row = []
                    for val in data[row_id]:
                        if isinstance(val, float):
                            new_row.append(round(val, round_digits))
                        else:
                            new_row.append(val)
                    data[row_id] = new_row
            writer.writerows(data)
        if print_message:
            print("Wrote file: {}".format(out_fname))
    except csv.Error:
        raise InvalidDataError("Check input data; Expected a list of values or list of lists of values.")


# Other input/output files

def read_csv_dict(d_file, ints=True, one_to_one=True, pdb_dict=False, str_float=False):
    """
    If an dictionary file is given, read it and return the dict[old]=new.
    Checks that all keys are unique.
    If one_to_one=True, checks that there 1:1 mapping of keys and values.

    :param d_file: the file with csv of old_id,new_id
    :param ints: boolean to indicate if the values are to be read as integers
    :param one_to_one: flag to check for one-to-one mapping in the dict
    :param pdb_dict: flag to format as required for the PDB output
    :param str_float: indicates dictionary is a string followed by a float
    :return: new_dict
    """
    new_dict = {}
    if pdb_dict:
        ints = False
        one_to_one = False
    elif str_float:
        ints = False
        one_to_one = False
        pdb_dict = False
    # If d_file is None, return the empty dictionary, as no dictionary file was specified
    base_fname = os.path.relpath(d_file)
    if d_file is not None:
        with open(d_file) as csv_file:
            reader = csv.reader(csv_file)
            key_count = 0
            for row in reader:
                if len(row) == 0:
                    continue
                if len(row) == 2:
                    if pdb_dict:
                        atom_type = row[0].strip()
                        if len(atom_type) < 4:
                            atom_type = " " + atom_type
                        elif len(atom_type) > 4:
                            raise InvalidDataError(f"Error reading line '{row}' in file: {base_fname}\n  "
                                                   f"Expected the atom type to have no more than 4 characters.")
                        element_type = row[1].strip()
                        if len(element_type) > 2:
                            raise InvalidDataError(f"Error reading line '{row}' in file: {base_fname}\n  "
                                                   f"Expected the element_type to have no more than 2 characters.")
                        new_dict[atom_type] = '{:>2s}'.format(element_type)
                    elif ints:
                        new_dict[int(row[0])] = int(row[1])
                    elif str_float:
                        new_dict[row[0]] = float(row[1])
                    else:
                        new_dict[row[0]] = row[1]
                    key_count += 1
                else:
                    raise InvalidDataError(f"Error reading line '{row}' in file: {base_fname}\n"
                                           f"  Expected exactly two comma-separated values per row.")
        if key_count == len(new_dict):
            if one_to_one:
                for key in new_dict:
                    if not (key in new_dict.values()):
                        raise InvalidDataError(f'Did not find a 1:1 mapping of key,val ids in file: {base_fname}')
        else:
            raise InvalidDataError(f'A non-unique key value (first column) found in file: {base_fname}')
    return new_dict


def create_element_dict(dict_file, pdb_dict=True, one_to_one=False):
    # This is used when need to add atom types to PDB file
    element_dict = {}
    if dict_file is not None:
        return read_csv_dict(dict_file, pdb_dict=pdb_dict, ints=False, one_to_one=one_to_one)
    return element_dict


def list_to_file(list_to_print, fname, list_format=None, delimiter=' ', mode='w', print_message=True):
    """
    Writes the list of sequences to the given file in the specified format for a PDB.

    :param list_to_print: A list of lines to print. The list may be a list of lists, list of strings, or a mixture.
    :param fname: The location of the file to write.
    :param list_format: Specified formatting for the line if the line is  list.
    :param delimiter: If no format is given and the list contains lists, the delimiter will join items in the list.
    :param print_message: boolean to determine whether to write to output if the file is printed or appended
    :param mode: write by default; can be changed to allow appending to file.
    """
    with open(fname, mode) as w_file:
        for line in list_to_print:
            # need to test for string first, because strings are iterable
            if isinstance(line, six.string_types):
                w_file.write(line + '\n')
            elif isinstance(line, Iterable):
                if list_format is None:
                    w_file.write(delimiter.join(map(str, line)) + "\n")
                else:
                    w_file.write(list_format.format(*line) + '\n')
            else:
                w_file.write(str(line) + '\n')
    if print_message:
        rel_path_fname = os.path.relpath(fname)
        if mode == 'w':
            print("Wrote file: {}".format(rel_path_fname))
        elif mode == 'a':
            print("  Appended: {}".format(rel_path_fname))


# def print_mm_kind(atom_type, radius, fname, mode='w'):
#     """
#     Writes the list to the given file, formatted for CP2K to read as qm atom indices.
#
#     :param atom_type: (str) MM atom type
#     :param radius: radius to list for covalent radius (smoothing point charge)
#     :param fname: The location of the file to write.
#     :param mode: default is to write to a new file. Use option to designate to append to existing file.
#     """
#     with open(fname, mode) as m_file:
#         m_file.write('    &MM_KIND {}\n'.format(atom_type))
#         m_file.write('        RADIUS {}\n'.format(radius))
#         m_file.write('    &END MM_KIND\n')
#     if mode == 'w':
#         print("Wrote file: {}".format(fname))
#
#
def print_qm_links(c_alpha_dict, c_beta_dict, f_name, mode="w"):
    """
    Note: this needs to be tested. Only ran once to get the protein residues set up correctly.
    :param c_alpha_dict: dict of protein residue to be broken to c_alpha atom id
    :param c_beta_dict: as above, but for c_beta
    :param f_name: The location of the file to write.
    :param mode: default is to write to a new file. Use option to designate to append to existing file.
    """
    with open(f_name, mode) as m_file:
        for resid in c_beta_dict:
            m_file.write('    !! Break resid {} between CA and CB, and cap CB with hydrogen\n'
                         '    &LINK\n       MM_INDEX  {}  !! CA\n       QM_INDEX  {}  !! CB\n'
                         '       LINK_TYPE  IMOMM\n       ALPHA_IMOMM  1.5\n'
                         '    &END LINK\n'.format(resid, c_alpha_dict[resid], c_beta_dict[resid]))
    if mode == 'w':
        print("Wrote file: {}".format(f_name))


# Conversions #

def to_int_list(raw_val):
    return_vals = []
    for val in raw_val.split(','):
        return_vals.append(int(val.strip()))
    return return_vals


def to_list(raw_val):
    return_vals = []
    for val in raw_val.split(','):
        return_vals.append(val.strip())
    return return_vals


def str_to_bool(s):
    """
    Basic converter for Python boolean values written as a str.
    :param s: The value to convert.
    :return: The boolean value of the given string.
    @raises: ValueError if the string value cannot be converted.
    """
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError("Cannot covert {} to a bool".format(s))


def fmt_row_data(raw_data, fmt_str):
    """ Formats the values in the dicts in the given list of raw data using
    the given format string.

    *This may not be needed at all*
    Now that I'm using csv.QUOTE_NONNUMERIC, generally don't want to format floats to strings

    :param raw_data: The list of dicts to format.
    :param fmt_str: The format string to use when formatting.
    :return: The formatted list of dicts.
    """
    fmt_rows = []
    for row in raw_data:
        fmt_row = {}
        for key, raw_val in row.items():
            fmt_row[key] = fmt_str.format(raw_val)
        fmt_rows.append(fmt_row)
    return fmt_rows


def conv_raw_val(param, def_val, int_list=True):
    """
    Converts the given parameter into the given type (default returns the raw value).  Returns the default value
    if the param is None.
    :param param: The value to convert.
    :param def_val: The value that determines the type to target.
    :param int_list: flag to specify if lists should converted to a list of integers
    :return: The converted parameter value.
    """
    if param is None:
        return def_val
    if isinstance(def_val, bool):
        if param in ['T', 't', 'true', 'TRUE', 'True']:
            return True
        else:
            return False
    if isinstance(def_val, int):
        return int(param)
    if isinstance(def_val, float):
        return float(param)
    if isinstance(def_val, list):
        if int_list:
            return to_int_list(param)
        else:
            return to_list(param)
    return param


def process_cfg(raw_cfg, def_cfg_vals=None, req_keys=None, int_list=True, store_extra_keys=False):
    """
    Converts the given raw configuration, filling in defaults and converting the specified value (if any) to the
    default value's type.
    :param raw_cfg: The configuration map.
    :param def_cfg_vals: dictionary of default values
    :param req_keys: dictionary of required types
    :param int_list: flag to specify if lists should converted to a list of integers
    :param store_extra_keys: boolean to skip error if there are unexpected keys
    :return: The processed configuration.

    """
    proc_cfg = {}
    extra_keys = []
    for key in raw_cfg:
        if not (key in def_cfg_vals or key in req_keys):
            if store_extra_keys:
                extra_keys.append(key)
            else:
                raise InvalidDataError("Unexpected key '{}' in configuration ('ini') file.".format(key))
    key = None
    try:
        for key, def_val in def_cfg_vals.items():
            proc_cfg[key] = conv_raw_val(raw_cfg.get(key), def_val, int_list)
        for key, type_func in req_keys.items():
            proc_cfg[key] = type_func(raw_cfg[key])
        for key in extra_keys:
            proc_cfg[key] = raw_cfg[key]
    except KeyError as e:
        raise KeyError("Missing config val for key '{}'".format(key, e))
    except Exception as e:
        raise InvalidDataError("Problem with config vals on key '{}': {}".format(key, e))

    return proc_cfg


def dequote(s):
    """
    from: http://stackoverflow.com/questions/3085382/python-how-can-i-strip-first-and-last-double-quotes
    If a string has single or double quotes around it, remove them.
    Make sure the pair of quotes match.
    If a matching pair of quotes is not found, return the string unchanged.
    """
    if isinstance(s, str) and len(s) > 0:
        if (s[0] == s[-1]) and s.startswith(("'", '"')):
            return s[1:-1]
    return s


def quote(s):
    """
    Converts a variable into a quoted string
    """
    if (s[0] == s[-1]) and s.startswith(("'", '"')):
        return str(s)
    return '"' + str(s) + '"'


def single_quote(s):
    """
    Converts a variable into a quoted string
    """
    if s[0] == s[-1]:
        if s.startswith("'") and s.endswith("'"):
            return str(s)
        elif s.startswith('"') and s.endswith('"'):
            s = dequote(s)
    return "'" + str(s) + "'"


# Comparisons #

def conv_num(s):
    if "_" in s:
        return s
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def diff_lines(floc1, floc2, delimiter=","):
    """
    Determine all lines in a file are equal.
    If only the following differences are found, the program will return a warning and an empty list
        -- floating point precision error (relative error within TOL)
        -- tailing while space
    :param floc1: file location 1
    :param floc2: file location 1
    :param delimiter: str, used to split lines to check for machine precision error
    :return: a list of the lines with differences
    """
    diff_lines_list = []
    # Save diffs to strings to be converted to use csv parser
    output_pos_dict = OrderedDict()
    output_neg_dict = OrderedDict()
    with open(floc1, 'r') as file1:
        with open(floc2, 'r') as file2:
            diff = list(difflib.ndiff(file1.read().splitlines(), file2.read().splitlines()))

    for line_num, line in enumerate(diff):
        if line.startswith('-') or line.startswith('+'):
            diff_lines_list.append(line)
            if line.startswith('-'):
                output_neg_dict[line_num] = line[2:]
            elif line.startswith('+'):
                output_pos_dict[line_num] = line[2:]

    if len(diff_lines_list) == 0:
        # First chance to leave program due to lack of differences
        return diff_lines_list

    warning("Checking for differences between files: {}\n          "
            "                                   and: {}".format(os.path.relpath(floc1), os.path.relpath(floc2)))
    pos_lines_nums = np.asarray(list(output_pos_dict.keys()))
    neg_lines_nums = np.asarray(list(output_neg_dict.keys()))

    if len(pos_lines_nums) != len(neg_lines_nums):
        return diff_lines_list

    incr = 100000
    for pot_incr in [2, -2, 1, -1, 3, -3]:
        # Account for offset made by difflib.ndiff when pointing out line differences
        if np.allclose(pos_lines_nums + pot_incr, neg_lines_nums):
            incr = pot_incr
            break
    # If still the original value, the IndexError will catch the resulting error

    # if the same number of lines, possible that differ only in order; can be helpful info for the user
    if output_pos_dict[pos_lines_nums[0]] == output_neg_dict[neg_lines_nums[0]]:
        warning("Check for line order differences.")
        return diff_lines_list

    white_space_diff = False
    precision_diff = False
    try:
        for line_num in pos_lines_nums:
            # Check for differences in tailing white space (this method ignores them)
            # check if difference is due to floating point precision. Before using the CSV reader, remove
            #   types of parenthesis only if in both.
            pos_line = output_pos_dict[line_num].rstrip()
            neg_line = output_neg_dict[line_num + incr].rstrip()
            if neg_line == pos_line:
                del output_pos_dict[line_num]
                del output_neg_dict[line_num + incr]
                white_space_diff = True
                continue
            for char in '(', ')', '[', ']', '{', '}':
                if char in pos_line and char in neg_line:
                    pos_line = pos_line.replace(char, "")
                    neg_line = neg_line.replace(char, "")
            # floats to ints makes life easier
            pos_line_list = list(csv.reader([pos_line], delimiter=delimiter))[0]
            neg_line_list = list(csv.reader([neg_line], delimiter=delimiter))[0]
            if len(pos_line_list) != len(neg_line_list):
                return diff_lines_list
            for pos, neg in zip(pos_line_list, neg_line_list):
                if pos == neg:
                    continue
                else:
                    pos = float(pos)
                    neg = float(neg)
                    if np.isclose(pos, neg, rtol=TOL, equal_nan=True):
                        continue
                    else:
                        return diff_lines_list
            # if didn't return by now, safe to delete the line
            del output_pos_dict[line_num]
            del output_neg_dict[line_num + incr]
            precision_diff = True
        if len(output_pos_dict) == 0 and len(output_pos_dict) == len(output_neg_dict):
            if white_space_diff:
                warning("Files differ in trailing white space.")
            if precision_diff:
                warning("Files differ in floating point precision.")
            return []
    except (ValueError, IndexError, TypeError, KeyError):
        return diff_lines_list

    return diff_lines_list  # likely never get here, but it doesn't hurt...


# Data Structures #

def unique_list(a_hashable):
    """ Creates an ordered (not_sorted) list from a list of tuples or other hashable items.
    From https://code.activestate.com/recipes/576694/#c6
    # if used, check if np.unique can do this
    """
    m_map = {}
    o_set = []
    for item in a_hashable:
        if item not in m_map:
            m_map[item] = 1
            o_set.append(item)
    return o_set


def conv_str_to_func(func_name):
    """
    Convert a name of a function into a function, if possible
    :param func_name: string to be converted (if possible)
    :return: either the function or error
    """
    name_func_dict = {"None": None,
                      "str": str,
                      "int": int,
                      "float": float,
                      "bool": bool,
                      }
    if func_name is None:
        return func_name
    elif func_name in name_func_dict:
        return name_func_dict[func_name]
    else:
        option_str = "', '".join(name_func_dict.keys())
        raise InvalidDataError(f"Invalid type entry '{func_name}'. Valid options are: '{option_str}'")


def process_pdb_file(pdb_file, atom_info_only=False):
    """
    Reads pdb_file data and returns in a dictionary format
    :param pdb_file: str, the location of the file to be read
    :param atom_info_only: boolean, whether to read the atom coordinates only or all atom data
    :return: pdb_data, dict organizing pdb data by section
    """
    pdb_data = {NUM_ATOMS: 0, SEC_HEAD: [], SEC_ATOMS: [], SEC_TAIL: []}
    if atom_info_only:
        pdb_data[SEC_ATOMS] = {}
    atom_id = 0

    with open(pdb_file) as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            line_head = line[:PDB_LINE_TYPE_LAST_CHAR]
            # head_content to contain Everything before 'Atoms' section
            # also capture the number of atoms
            # match 5 letters so don't need to set up regex for the ones that have numbers following the letters
            # noinspection SpellCheckingInspection
            if line_head[:-1] in ['HEADE', 'TITLE', 'REMAR', 'CRYST', 'MODEL', 'COMPN',
                                  'NUMMD', 'ORIGX', 'SCALE', 'SOURC', 'AUTHO', 'CAVEA',
                                  'EXPDT', 'MDLTY', 'KEYWD', 'OBSLT', 'SPLIT', 'SPRSD',
                                  'REVDA', 'JRNL ', 'DBREF', 'SEQRE', 'HET  ', 'HETNA',
                                  'HETSY', 'FORMU', 'HELIX', 'SHEET', 'SSBON', 'LINK ',
                                  'CISPE', 'SITE ', ]:
                # noinspection PyTypeChecker
                pdb_data[SEC_HEAD].append(line)

            # atoms_content to contain everything but the xyz
            elif line_head == 'ATOM  ' or line_head == 'HETATM':

                # By renumbering, handles the case when a PDB template has ***** after atom_id 99999.
                # For renumbering, making sure prints in the correct format, including num of characters:
                atom_id += 1
                if atom_id > 99999:
                    atom_num = format(atom_id, 'x')
                else:
                    atom_num = '{:5d}'.format(atom_id)
                # Alternately, use this:
                # atom_num = line[cfg[PDB_LINE_TYPE_LAST_CHAR]:cfg[PDB_ATOM_NUM_LAST_CHAR]]

                atom_type = line[PDB_ATOM_NUM_LAST_CHAR:PDB_ATOM_TYPE_LAST_CHAR]
                res_type = line[PDB_ATOM_TYPE_LAST_CHAR:PDB_RES_TYPE_LAST_CHAR]
                mol_num = int(line[PDB_RES_TYPE_LAST_CHAR:PDB_MOL_NUM_LAST_CHAR])
                pdb_x = float(line[PDB_MOL_NUM_LAST_CHAR:PDB_X_LAST_CHAR])
                pdb_y = float(line[PDB_X_LAST_CHAR:PDB_Y_LAST_CHAR])
                pdb_z = float(line[PDB_Y_LAST_CHAR:PDB_Z_LAST_CHAR])
                last_cols = line[PDB_Z_LAST_CHAR:]
                element_type = line[PDB_BEFORE_ELE_LAST_CHAR:PDB_ELE_LAST_CHAR]

                if atom_info_only:
                    atom_xyz = np.array([pdb_x, pdb_y, pdb_z])
                    pdb_data[SEC_ATOMS][atom_id] = {ATOM_TYPE: element_type, ATOM_COORDS: atom_xyz}
                else:
                    line_struct = [line_head, atom_num, atom_type, res_type, mol_num, pdb_x, pdb_y, pdb_z, last_cols]
                    # noinspection PyTypeChecker
                    pdb_data[SEC_ATOMS].append(line_struct)
            elif line_head == 'END':
                pdb_data[SEC_TAIL].append(line)
                break
            # tail_content to contain everything after the 'Atoms' section
            else:
                # noinspection PyTypeChecker
                pdb_data[SEC_TAIL].append(line)
    pdb_data[NUM_ATOMS] = len(pdb_data[SEC_ATOMS])
    return pdb_data


def longest_common_substring(s1, s2):
    """
    From https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring#Python
    :param s1: string 1
    :param s2: string 2
    :return: string: the longest common string!
    """
    # noinspection PyUnusedLocal
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]


def assign_color(int_val):
    """
    Given an integer, return a color; this function allows repeating colors instead of getting an index error if the
    index is greater than the length of the color array
    :param int_val: int, can be zero
    :return:
    """
    num_colors = len(COLOR_SEQUENCE)
    # catch int = 0, then return the first color
    if int_val:
        color_idx = int_val % num_colors
        return COLOR_SEQUENCE[color_idx]
    else:
        return COLOR_SEQUENCE[0]


# FIGURES

def save_figure(f_name, print_msg=True):
    """
    Specifies where and if to save a created figure
    :param f_name: str, name for the file
    :param print_msg: boolean as to whether to print a note that a figure was saved
    :return: n/a
    """
    plt.savefig(f_name, bbox_inches='tight', transparent=True)
    if print_msg:
        print("Wrote file: {}".format(os.path.relpath(f_name)))


def make_fig(fname, x_array, y1_array, y1_label="", ls1="-", color1=COLORBREWER_BLUE,
             x2_array=None, y2_array=None, y2_label="", ls2='--', color2=COLORBREWER_ORANGE,
             x3_array=None, y3_array=None, y3_label="", ls3=':', color3=COLORBREWER_GREEN,
             x4_array=None, y4_array=None, y4_label="", ls4='-.', color4=COLORBREWER_RED,
             x5_array=None, y5_array=None, y5_label="", ls5='-', color5=COLORBREWER_PURPLE,
             x_fill=None, y_fill=None, x2_fill=None, y2_fill=None,
             fill1_label=None, fill2_label=None,
             fill_color_1="green", fill_color_2="blue",
             x_label="", y_label="", x_lima=None, x_limb=None, y_lima=None, y_limb=None, loc=0,
             fig_width=DEF_FIG_WIDTH, fig_height=DEF_FIG_HEIGHT, axis_font_size=DEF_AXIS_SIZE,
             tick_font_size=DEF_TICK_SIZE, hide_x=False, title="", print_msg=True):
    """
    Many defaults to provide flexibility
    """
    # rc('text', usetex=True)
    # a general purpose plotting routine; can plot between 1 and 5 curves
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.plot(x_array, y1_array, ls1, label=y1_label, linewidth=2, color=color1)
    if y2_array is not None:
        if x2_array is None:
            x2_array = x_array
        ax.plot(x2_array, y2_array, label=y2_label, ls=ls2, linewidth=2, color=color2)
    if y3_array is not None:
        if x3_array is None:
            x3_array = x_array
        ax.plot(x3_array, y3_array, label=y3_label, ls=ls3, linewidth=3, color=color3)
    if y4_array is not None:
        if x4_array is None:
            x4_array = x_array
        ax.plot(x4_array, y4_array, label=y4_label, ls=ls4, linewidth=3, color=color4)
    if y5_array is not None:
        if x5_array is None:
            x5_array = x_array
        ax.plot(x5_array, y5_array, label=y5_label, ls=ls5, linewidth=3, color=color5)
    ax.set_xlabel(x_label, fontsize=axis_font_size)
    ax.set_ylabel(y_label, fontsize=axis_font_size)
    if x_limb is not None:
        if x_lima is None:
            x_lima = 0.0
        ax.set_xlim([x_lima, x_limb])

    if y_limb is not None:
        if y_lima is None:
            y_lima = 0.0
        ax.set_ylim([y_lima, y_limb])

    if x_fill is not None:
        plt.fill_between(x_fill, y_fill, 0, color=fill_color_1, alpha='0.75')

    if x2_fill is not None:
        plt.fill_between(x2_fill, y2_fill, 0, color=fill_color_2, alpha='0.5')

    if title:
        ax.set_title(title, fontsize=axis_font_size)
    ax.tick_params(labelsize=tick_font_size)
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    if len(y1_label) > 0:
        ax.legend(loc=loc, fontsize=tick_font_size, )
    if fill1_label and fill2_label:
        p1 = Rectangle((0, 0), 1, 1, fc=fill_color_1, alpha=0.75)
        p2 = Rectangle((0, 0), 1, 1, fc=fill_color_2, alpha=0.5)
        ax.legend([p1, p2], [fill1_label, fill2_label], loc=loc, fontsize=tick_font_size, )
    if hide_x:
        ax.xaxis.set_visible(False)
    else:
        ax.xaxis.grid(True, 'minor')
        ax.xaxis.grid(True, 'major')
    # ax.yaxis.grid(True, 'minor')
    # ax.yaxis.grid(True, 'major', linewidth=1)
    save_figure(fname, print_msg)
    plt.close()


# specifically for chemistry

def calc_mass_from_formula(mol_formula):
    stoich_dict = parse_stoich(mol_formula)
    mol_mass = 0
    for atom_type, num_atoms in stoich_dict.items():
        mass_most_abundant_isotope = ISOTOPE_MASS_DICT[atom_type][MASS][0]
        mol_mass += mass_most_abundant_isotope * num_atoms
    return mol_mass


def parse_stoich(stoich_string, add_to_dict=None):
    raw_list = re.findall(r'([A-Z][a-z]*)(\d*)', stoich_string)
    stoich_dict = {}
    for atom_tuple in raw_list:
        if atom_tuple[1] == '':
            stoich_dict[atom_tuple[0]] = 1
        else:
            stoich_dict[atom_tuple[0]] = int(atom_tuple[1])
    if add_to_dict:
        for key, val in add_to_dict.items():
            if key in stoich_dict:
                stoich_dict[key] += add_to_dict[key]
            else:
                stoich_dict[key] = add_to_dict[key]
    return stoich_dict
