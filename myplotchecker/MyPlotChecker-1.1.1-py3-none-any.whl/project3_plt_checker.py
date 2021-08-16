"""
Plot checker for Project 3 of Rice CS DataViz course

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
    binary = pkgutil.get_data(__name__, 'project3_plt_tests.pickle')
    plt_tests = pickle.loads(binary)

    global student_module
    student_module = import_nb(student_nb_path)


# ------
# Methods checking the student's module
# ------

def check_plot_price():
    """
    Check the plot_price() method in the solution module

    Inputs
        solution - Python module

    Actions
        1. Print a message about the result
        2. add variables 'plot_price' (summary of the figure) and 'plot_price_img' (image of the figure)
           to the global environment
    """

    # Universal Chart Specification for plot_price()
    # Checks only the bold part of the rubric

    y_axis_spec = OrderedDict(
            type='Y',
            range=match_array(),
            tick_locations=is_evenly_spaced(),
            label={'text': contains_keyword('price', OR('dollars', '$', 'USD'))},
    )

    subplot_spec = OrderedDict(
            meshes=match_mesh_lists(),
            axes=[{}, y_axis_spec],
    )

    ucs = {'subplots': [subplot_spec]}

    # Convert and check plot_price()
    # Run the plot checker (both conversion to UCM and checking are done inside check_tests())

    checker_dict = {'plot_prices': (ucs, 8)}

    path_dict = {
        "plot_prices.subplots"                          : "the figure",
        "plot_prices.subplots[0]"                       : "the subplot",
        "plot_prices.subplots[0].axes"                  : "the list of axes",
        "plot_prices.subplots[0].axes[0]"               : "the x-axis",
        "plot_prices.subplots[0].axes[1]"               : "the y-axis",
        "plot_prices.subplots[0].axes[1].type"          : "the second axis's type",
        "plot_prices.subplots[0].axes[1].label"         : "the y-axis's label",
        "plot_prices.subplots[0].axes[1].label.text"    : "the y-axis's label",
        "plot_prices.subplots[0].axes[1].range"         : "the y-axis's range",
        "plot_prices.subplots[0].axes[1].tick_locations": "the y-axis's ticks",
        "plot_prices.subplots[0].meshes"                : "lineplots",
    }

    plt_tests.check_tests(student_module, checker_dict, path_dict, nb_env)


def check_plot_dates_price():
    """
    Check the plot_dates_price() method in the solution module

    Inputs
        solution - Python module

    Actions
        1. Print a message about the result
        2. add variables 'plot_dates_price' (summary of the figure) and 'plot_dates_price_img' (image of the figure)
           to the global environment
    """

    # Universal Chart Specification for plot_dates_price()
    # Checks only the bold part of the rubric

    x_axis_spec = OrderedDict(
            type='X',
            # tick_labels={'.*': {'text': match_object()}},        # result is different for old Matplotlib on Vocareum and the new one
            label={'text': contains_keyword(OR('date', 'time', 'year'))},
    )

    y_axis_spec = OrderedDict(
            type='Y',
            range=match_array(),
            tick_locations=is_evenly_spaced(),
            label={'text': contains_keyword('price', OR('dollar', '$', 'USD'))},
    )

    subplot_spec = OrderedDict(
            meshes=match_mesh_lists(),
            axes=[x_axis_spec, y_axis_spec],
    )

    plot_dates_prices_ucs = {'subplots': [subplot_spec]}

    # Convert and check plot_two_indices()
    # Run the plot checker (both conversion to UCM and checking are done inside check_tests())

    checker_dict = {'plot_dates_prices': (plot_dates_prices_ucs, 8)}

    path_dict = {
        "plot_dates_prices.subplots"                               : "the figure",
        "plot_dates_prices.subplots[0]"                            : "the subplot",
        "plot_dates_prices.subplots[0].axes"                       : "the list of axes",
        "plot_dates_prices.subplots[0].axes[0]"                    : "the x-axis",
        "plot_dates_prices.subplots[0].axes[0].type"               : "the first axis's type",
        "plot_dates_prices.subplots[0].axes[0].label"              : "the x-axis's label",
        "plot_dates_prices.subplots[0].axes[0].label.text"         : "the x-axis's label",
        "plot_dates_prices.subplots[0].axes[0].tick_labels"        : "the x-axis's ticks",
        "plot_dates_prices.subplots[0].axes[0].tick_labels..*"     : "the x-axis's ticks",
        "plot_dates_prices.subplots[0].axes[0].tick_labels..*.text": "the x-axis's ticks",
        "plot_dates_prices.subplots[0].axes[1]"                    : "the y-axis",
        "plot_dates_prices.subplots[0].axes[1].type"               : "the second axis's type",
        "plot_dates_prices.subplots[0].axes[1].label"              : "the y-axis's label",
        "plot_dates_prices.subplots[0].axes[1].label.text"         : "the y-axis's label",
        "plot_dates_prices.subplots[0].axes[1].range"              : "the y-axis's range",
        "plot_dates_prices.subplots[0].axes[1].tick_locations"     : "the y-axis's ticks",
        "plot_dates_prices.subplots[0].meshes"                     : "lineplots"}

    plt_tests.check_tests(student_module, checker_dict, path_dict, nb_env)


def check_plot_two_indices():
    """
    Check the plot_two_indices() method in the solution module

    Inputs
        solution - Python module

    Actions
        1. Print a message about the result
        2. add variables 'plot_two_indices' (summary of the figure) and 'plot_two_indices_img' (image of the figure)
           to the global environment
    """

    # Universal Chart Specification for plot_two_indices()
    # Checks only the bold part of the rubric

    x_axis_spec = OrderedDict(
            type='X',
            label={'text': contains_keyword(OR('date', 'time', 'year'))}
    )

    y_axis_spec = OrderedDict(
            type='Y',
            range=match_array(),
            tick_locations=is_evenly_spaced(),
            label={'text': contains_keyword('price', OR('dollar', '$', 'USD'))},
    )

    subplot_spec = OrderedDict(
            meshes=match_mesh_lists(),
            axes=[x_axis_spec, y_axis_spec, y_axis_spec],
    )

    plot_two_indices_ucs = {'subplots': [subplot_spec]}

    # Convert and check plot_two_indices()
    # Run the plot checker (both conversion to UCM and checking are done inside check_tests())

    checker_dict = {'plot_two_indices': (plot_two_indices_ucs, 8)}

    path_dict = {
        "plot_two_indices.subplots"                          : "the figure",
        "plot_two_indices.subplots[0]"                       : "the subplot",
        "plot_two_indices.subplots[0].axes"                  : "the list of axes",
        "plot_two_indices.subplots[0].axes[0]"               : "the x-axis",
        "plot_two_indices.subplots[0].axes[0].label"         : "the x-axis's label",
        "plot_two_indices.subplots[0].axes[0].label.text"    : "the x-axis's label",
        "plot_two_indices.subplots[0].axes[0].type"          : "the first axis's type",
        "plot_two_indices.subplots[0].axes[1]"               : "the left x-axis",
        "plot_two_indices.subplots[0].axes[1].label"         : "the left y-axis's label",
        "plot_two_indices.subplots[0].axes[1].label.text"    : "the left y-axis's label",
        "plot_two_indices.subplots[0].axes[1].range"         : "the left y-axis's range",
        "plot_two_indices.subplots[0].axes[1].tick_locations": "the left y-axis's ticks",
        "plot_two_indices.subplots[0].axes[1].type"          : "the second axis's type",
        "plot_two_indices.subplots[0].axes[2]"               : "the right y-axis",
        "plot_two_indices.subplots[0].axes[2].label"         : "the right y-axis's label",
        "plot_two_indices.subplots[0].axes[2].label.text"    : "the right y-axis's label",
        "plot_two_indices.subplots[0].axes[2].range"         : "the right y-axis's range",
        "plot_two_indices.subplots[0].axes[2].tick_locations": "the right y-axis's ticks",
        "plot_two_indices.subplots[0].axes[2].type"          : "the third axis's type",
        "plot_two_indices.subplots[0].meshes"                : "lineplots"}

    plt_tests.check_tests(student_module, checker_dict, path_dict, nb_env)