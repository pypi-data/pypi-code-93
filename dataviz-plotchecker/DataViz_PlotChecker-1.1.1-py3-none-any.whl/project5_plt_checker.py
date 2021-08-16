"""
Plot checker for Project 5 of Rice CS DataViz course

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
    binary = pkgutil.get_data(__name__, 'project5_plt_tests.pickle')
    plt_tests = pickle.loads(binary)

    global student_module
    student_module = import_nb(student_nb_path)


# ------
# Methods checking the student's module
# ------

def check_plot_julia():
    """
    Check the plot_julia() method in the solution module

    Inputs
        solution - Python module

    Actions
        1. Print a message about the result
        2. add variables 'plot_julia' (summary of the figure) and 'plot_julia_img' (image of the figure)
           to the global environment
    """

    # Universal Chart Specification for plot_julia()
    # Checks only the bold part of the rubric

    x_axis_spec = OrderedDict(
            type='X',
            range=match_array(rtol=0.2),
            tick_locations=is_evenly_spaced(),
            label={'text': contains_keyword('real')},
    )

    y_axis_spec = OrderedDict(
            type='Y',
            range=match_array(rtol=0.2),
            tick_locations=is_evenly_spaced(),
            label={'text': contains_keyword('imag')},
    )

    subplot_spec = OrderedDict(
            meshes=match_meshes(),
            axes=[x_axis_spec, y_axis_spec],
            title={'text': contains_keyword(OR('λ', 'lambda'))},
    )

    plot_julia_ucs = {'subplots': [subplot_spec]}

    # Convert and check plot_julia()
    # Run the plot checker (both conversion to UCM and checking are done inside check_tests())

    checker_dict = {'plot_julia': (plot_julia_ucs, 8)}

    path_dict = {
        "plot_julia"                                   : "The figure",
        "plot_julia.subplots"                          : "The subplot",
        "plot_julia.subplots[0]"                       : "The subplot",
        "plot_julia.subplots[0].axes"                  : "The list of axes",
        "plot_julia.subplots[0].axes[0]"               : "The x-axis",
        "plot_julia.subplots[0].axes[0].type"          : "The first axis's type",
        "plot_julia.subplots[0].axes[0].label"         : "The x-axis's label",
        "plot_julia.subplots[0].axes[0].label.text"    : "The x-axis's label",
        "plot_julia.subplots[0].axes[0].tick_locations": "The x-axis's ticks",
        "plot_julia.subplots[0].axes[1]"               : "The y-axis",
        "plot_julia.subplots[0].axes[1].type"          : "The second axis's type",
        "plot_julia.subplots[0].axes[1].label"         : "The y-axis's label",
        "plot_julia.subplots[0].axes[1].label.text"    : "The y-axis's label",
        "plot_julia.subplots[0].axes[1].tick_locations": "The y-axis's ticks",
        "plot_julia.subplots[0].meshes"                : "The scatter plot",
        "plot_julia.subplots[0].title"                 : "The subplot title",
        "plot_julia.subplots[0].title.text"            : "The subplot title"}

    plt_tests.check_tests(student_module, checker_dict, path_dict, nb_env)


def check_plot_mandel():
    """
    Check the plot_mandelbrot() method in the solution module

    Inputs
        solution - Python module

    Actions
        1. Print a message about the result
        2. add variables 'plot_mandelbrot' (summary of the figure) and 'plot_mandelbrot_img' (image of the figure)
           to the global environment
    """

    # Universal Chart Specification for plot_mandelbrot()
    # Checks only the bold part of the rubric

    x_axis_spec = OrderedDict(
            type='X',
            range=match_array(rtol=0.2),
            label={'text': contains_keyword('real')},
    )

    y_axis_spec = OrderedDict(
            type='Y',
            range=match_array(rtol=0.2),
            label={'text': contains_keyword('imag')},
    )

    grids_spec = OrderedDict(
            type='Image2D',
            extents=match_array(),
            vals=match_array(),
    )

    subplot_spec = OrderedDict(
            grids=[grids_spec],
            axes=[x_axis_spec, y_axis_spec],
            title={'text': contains_keyword('mandel')},
    )

    plot_mandelbrot_ucs = {'subplots': [subplot_spec]}

    # Convert and check plot_mandelbrot()
    # Run the plot checker (both conversion to UCM and checking are done inside check_tests())

    checker_dict = {'plot_mandelbrot': (plot_mandelbrot_ucs, 8)}

    path_dict = {
        "plot_mandelbrot"                               : "The figure",
        "plot_mandelbrot.subplots"                      : "The subplot",
        "plot_mandelbrot.subplots[0]"                   : "The subplot",
        "plot_mandelbrot.subplots[0].axes"              : "The list of axes",
        "plot_mandelbrot.subplots[0].axes[0]"           : "The x-axis",
        "plot_mandelbrot.subplots[0].axes[0].type"      : "The first axis's type",
        "plot_mandelbrot.subplots[0].axes[0].label"     : "The x-axis's label",
        "plot_mandelbrot.subplots[0].axes[0].label.text": "The x-axis's label",
        "plot_mandelbrot.subplots[0].axes[1]"           : "The y-axis",
        "plot_mandelbrot.subplots[0].axes[1].type"      : "The second axis's type",
        "plot_mandelbrot.subplots[0].axes[1].label"     : "The y-axis's label",
        "plot_mandelbrot.subplots[0].axes[1].label.text": "The y-axis's label",
        "plot_mandelbrot.subplots[0].grids"             : "The raster image",
        "plot_mandelbrot.subplots[0].grids[0]"          : "The raster image",
        "plot_mandelbrot.subplots[0].grids[0].vals"     : "The pixels of the raster image",
        "plot_mandelbrot.subplots[0].grids[0].extents"  : "extents of the raster image",
        "plot_mandelbrot.subplots[0].title"             : "The subplot title",
        "plot_mandelbrot.subplots[0].title.text"        : "The subplot title"}

    plt_tests.check_tests(student_module, checker_dict, path_dict, nb_env)


def check_plot_newton():
    """
    Check the plot_newton() method in the solution module

    Inputs
        solution - Python module

    Actions
        1. Print a message about the result
        2. add variables 'plot_newton' (summary of the figure) and 'plot_newton_img' (image of the figure)
           to the global environment
    """

    # Universal Chart Specification for plot_newton()
    # Checks only the bold part of the rubric

    x_axis_spec = OrderedDict(
            range=match_array(rtol=0.2),
            label={'text': contains_keyword('real')},
    )

    y_axis_spec = OrderedDict(
            range=match_array(rtol=0.2),
            label={'text': contains_keyword('imag')},
    )

    grids_spec = OrderedDict(
            type='Image2D',
            extents=match_array(),
            vals=match_array(),
    )

    subplot_spec = OrderedDict(
            grids=[grids_spec],
            meshes=match_meshes(),
            axes=[x_axis_spec, y_axis_spec],
            title={'text': contains_keyword('newton')},
    )

    plot_newton_ucs = {'subplots': [subplot_spec]}

    # Convert and check plot_newton()
    # Run the plot checker (both conversion to UCM and checking are done inside check_tests())

    checker_dict = {'plot_newton': (plot_newton_ucs, 8)}

    path_dict = {
        "plot_newton"                               : "The figure",
        "plot_newton.subplots"                      : "The subplot",
        "plot_newton.subplots[0]"                   : "The subplot",
        "plot_newton.subplots[0].axes"              : "The list of axes",
        "plot_newton.subplots[0].axes[0]"           : "The x-axis",
        "plot_newton.subplots[0].axes[0].type"      : "The first axis's type",
        "plot_newton.subplots[0].axes[0].label"     : "The x-axis's label",
        "plot_newton.subplots[0].axes[0].label.text": "The x-axis",
        "plot_newton.subplots[0].axes[1]"           : "The y-axis",
        "plot_newton.subplots[0].axes[1].type"      : "The second axis's type",
        "plot_newton.subplots[0].axes[1].label"     : "The y-axis's label",
        "plot_newton.subplots[0].axes[1].label.text": "The y-axis's label",
        "plot_newton.subplots[0].grids"             : " The raster image",
        "plot_newton.subplots[0].grids[0]"          : "The raster image",
        "plot_newton.subplots[0].grids[0].vals"     : "The pixels of the raster image",
        "plot_newton.subplots[0].grids[0].extents"  : "extents of the raster image",
        "plot_newton.subplots[0].meshes"            : "scatter plot of the roots",
        "plot_newton.subplots[0].title"             : "The subplot title",
        "plot_newton.subplots[0].title.text"        : "The subplot title"}

    plt_tests.check_tests(student_module, checker_dict, path_dict, nb_env)
