"""
Plot checker for Project 4 of Rice CS DataViz course

This module simulates a singleton class

Author: Zion (Zion.Yang@rice.edu)
Last updated: 2021/08/02
"""

import pkgutil
from collections import OrderedDict

import dill as pickle

from import_nb import import_nb
from plt_checker.core import PlotTests
from plt_checker.atomic_methods import *

# Global variables
nb_env: dict = None  # capture notebook environment
plt_tests: PlotTests = None  # Test cases for the plot checker
student_module = None


def init(student_nb_path: str, env: dict):
    """
    Populate the global variables

    Args
        student_nb_path - the path of student notebook to check
        env - value of globals() in the Jupyter notebook
    """

    global nb_env
    nb_env = env

    global plt_tests
    binary = pkgutil.get_data(__name__, 'project4_plt_tests.pickle')
    plt_tests = pickle.loads(binary)

    global student_module
    student_module = import_nb(student_nb_path)


# ------
# Methods checking the student's module
# ------

def check_plot_earth_coords():
    """
    Check the plot_earth_coords() method in the solution module

    Inputs
        solution - Python module

    Actions
        1. Print a message about the result
        2. add variables 'plot_earth_coords' (summary of the figure) and 'plot_earth_coords_img' (image of the figure)
           to the global environment
    """

    # Universal Chart Specification for plot_earth_coords()
    # Checks only the bold part of the rubric

    x_axis_spec = OrderedDict(
            type='X',
            label={'text': contains_keyword('day')}
    )

    y_axis_spec = OrderedDict(
            type='Y',
            label={'text': contains_keyword(OR('kilometer', 'km'))},
    )

    subplot_spec = OrderedDict(
            meshes=match_meshes(),
            axes=[x_axis_spec, y_axis_spec],
            legends=[{}],
            title={'text': contains_keyword('coordinate', 'day')},
    )

    plot_earth_coords_ucs = {'subplots': [subplot_spec]}

    # Convert and check plot_earth_coords()
    # Run the plot checker (both conversion to UCM and checking are done inside check_tests())

    checker_dict = {'plot_earth_coords': (plot_earth_coords_ucs, 8)}

    path_dict = {
        "plot_earth_coords.subplots"                      : "the figure",
        "plot_earth_coords.subplots[0]"                   : "the subplot",
        "plot_earth_coords.subplots[0].axes"              : "the list of axes",
        "plot_earth_coords.subplots[0].axes[0]"           : "the x-axis",
        "plot_earth_coords.subplots[0].axes[0].label"     : "the x-axis's label",
        "plot_earth_coords.subplots[0].axes[0].label.text": "the x-axis's label",
        "plot_earth_coords.subplots[0].axes[0].type"      : "the first axis's type",
        "plot_earth_coords.subplots[0].axes[1]"           : "the y-axis",
        "plot_earth_coords.subplots[0].axes[1].label"     : "the y-axis",
        "plot_earth_coords.subplots[0].axes[1].label.text": "the y-axis's label",
        "plot_earth_coords.subplots[0].axes[1].type"      : "the second axis's type",
        "plot_earth_coords.subplots[0].legends"           : "legend(s) attached to subplot",
        "plot_earth_coords.subplots[0].legends[0]"        : "the Legend attached to subplot",
        "plot_earth_coords.subplots[0].meshes"            : "lineplots",
        "plot_earth_coords.subplots[0].title"             : "the subplot title",
        "plot_earth_coords.subplots[0].title.text"        : "the subplot title"}

    plt_tests.check_tests(student_module, checker_dict, path_dict, nb_env)


def check_plot_earth_orbit():
    """
    Check the plot_earth_orbit() method in the solution module

    Inputs
        solution - Python module

    Actions
        1. Print a message about the result
        2. add variables 'plot_earth_orbit' (summary of the figure) and 'plot_earth_orbit_img' (image of the figure)
           to the global environment
    """

    # Universal Chart Specification for plot_earth_orbit()
    # Checks only the bold part of the rubric

    x_axis_spec = OrderedDict(
            type='X',
            tick_locations=is_evenly_spaced(),
            label={'text': contains_keyword(OR('kilometer', 'km'))},
    )

    y_axis_spec = OrderedDict(
            type='Y',
            tick_locations=is_evenly_spaced(),
            label={'text': contains_keyword(OR('kilometer', 'km'))},
    )

    subplot_spec = OrderedDict(
            meshes=match_meshes(),
            axes=[x_axis_spec, y_axis_spec],
            display_range=match_aspect_ratio(),
            title={'text': contains_keyword('orbit', 'day')},
    )

    plot_earth_orbit_ucs = {'subplots': [subplot_spec]}

    # Convert and check plot_earth_orbit()
    # Run the plot checker (both conversion to UCM and checking are done inside check_tests())

    checker_dict = {'plot_earth_orbit': (plot_earth_orbit_ucs, 8)}

    path_dict = {
        "plot_earth_orbit.subplots"                          : "the figure",
        "plot_earth_orbit.subplots[0]"                       : "the subplot",
        "plot_earth_orbit.subplots[0].axes"                  : "the list of axes",
        "plot_earth_orbit.subplots[0].axes[0]"               : "the x-axis",
        "plot_earth_orbit.subplots[0].axes[0].label"         : "the x-axis's label",
        "plot_earth_orbit.subplots[0].axes[0].label.text"    : "the x-axis's label",
        "plot_earth_orbit.subplots[0].axes[0].tick_locations": "the x-axis's ticks",
        "plot_earth_orbit.subplots[0].axes[0].type"          : "the first axis's type",
        "plot_earth_orbit.subplots[0].axes[1]"               : "the y-axis",
        "plot_earth_orbit.subplots[0].axes[1].label"         : "the y-axis's label",
        "plot_earth_orbit.subplots[0].axes[1].label.text"    : "the y-axis's label",
        "plot_earth_orbit.subplots[0].axes[1].tick_locations": "the y-axis's ticks",
        "plot_earth_orbit.subplots[0].axes[1].type"          : "the second axis's type",
        "plot_earth_orbit.subplots[0].display_range"         : "the size of figure in display coordinates",
        "plot_earth_orbit.subplots[0].meshes"                : "orbit",
        "plot_earth_orbit.subplots[0].title"                 : "the subplot title",
        "plot_earth_orbit.subplots[0].title.text"            : "the subplot title"}

    plt_tests.check_tests(student_module, checker_dict, path_dict, nb_env)
