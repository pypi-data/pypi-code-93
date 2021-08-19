"""
Common functions for Python / Vue / Eel project.

It contains functions for running eel, overriding eel.expose decorator, converting json to correct python
format or transform data into form for vue tables and plots.

Go on

https://mypythontools.readthedocs.io/#project-starter

for example with working examples.

Image of such an app

.. image:: /_static/project-starter-gui.png
    :width: 620
    :alt: project-starter-gui
    :align: center

"""

import os
import sys
from pathlib import Path
import warnings


import mylogging

from . import paths
from . import misc

# Lazy imports
# import numpy as np
# import inspect
# import ast

# import pandas as pd
# import EelForkExcludeFiles as eel


eel = None

expose_error_callback = None
json_to_py = misc.json_to_py


def run_gui(devel=None, log_file_path=None, is_multiprocessing=False, builded_gui_path="default"):
    """Function that init and run `eel` project.

    It will autosetup chrome mode (if installed chrome or chromium, open separate window with
    no url bar, no bookmarks etc...) if chrome is not installed, it open microsoft Edge (by default
    on windows).

    In devel mode, app is connected on live vue server. Serve your web application with node, debug python app file
    that calls this function (do not run, just debug - server could stay running after close and occupy used port). Open browser on 8080.

    Debugger should correctly stop at breakpoints if frontend run some python function.

    Note:
        Check project-starter on github for working examples and tutorial how to run.

        https://mypythontools.readthedocs.io/#project-starter

    Args:
        devel((bool, None), optional): If None, detected. Can be overwritten. Devel 0 run static assets, 1 run Vue server on localhost.
            Defaults to None.
        log_file_path ((str, Path, None)), optional): If not exist, it will create, if exist, it will append,
            if None, log to relative log.log and only if in production mode. Defaults to None.
        is_multiprocessing (bool, optional): If using multiprocessing in some library, set up to True. Defaults to False.
        builded_gui_path ((str, Path, None)), optional): Where the web asset is. Only if debug is 0 but not run with pyinstaller.
            If None, it's automatically find (but is slower then). If 'default', path from project-starter is used - 'gui/web_builded'
            is used. Defaults to 'default'.

    If you want to understand this technology more into detail, check this tutorial

    https://mypythontools.readthedocs.io/pyvueeel-tutorial.html
    """

    # Just for lazy load of eel for users that will not use this module
    global eel

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", module="EelForkExcludeFiles", category=ResourceWarning)

        import EelForkExcludeFiles as eel_library

    eel = eel_library

    try:
        if devel is None:
            # env var MY_PYTHON_VUE_ENVIRONMENT is configured and added with pyinstaller automatically in build module
            devel = False if os.environ.get("MY_PYTHON_VUE_ENVIRONMENT") == "production" else True

        # Whether run is from .exe or from python
        is_builded = True if getattr(sys, "frozen", False) else False

        if log_file_path:
            log_file = log_file_path
        else:
            log_file = "log.log" if is_builded else None

        mylogging.config.TO_FILE = log_file

        if is_builded:
            # gui folder is created with pyinstaller in build
            gui_path = Path(sys._MEIPASS) / "gui"
        else:
            if devel:
                paths.set_root()
                gui_path = (
                    paths.find_path("index.html", exclude=["node_modules", "build", "dist"]).parents[1]
                    / "src"
                )
            else:
                if builded_gui_path:
                    gui_path = Path(builded_gui_path)

                else:
                    paths.set_root()
                    gui_path = paths.find_path(
                        "index.html", exclude=["public", "node_modules", "build"]
                    ).parent

        if not gui_path.exists():
            raise FileNotFoundError("Web files not found, setup gui_path (where builded index.html is).")

        if devel:
            directory = gui_path
            app = None
            page = {"port": 8080}
            port = 8686
            init_files = [".vue", ".js", ".html"]

            def close_callback(page, sockets):
                pass

        else:
            directory = gui_path
            close_callback = None
            app = "chrome"
            page = "index.html"
            port = 0
            init_files = [".js", ".html"]

        eel.init(directory.as_posix(), init_files, exlcude_patterns=["chunk-vendors"])

        if is_multiprocessing:
            from multiprocessing import freeze_support

            freeze_support()

        mylogging.info("Py side started")

        eel.start(
            page,
            mode=app,
            cmdline_args=["--disable-features=TranslateUI"],
            close_callback=close_callback,
            host="localhost",
            port=port,
            disable_cache=True,
        ),

    except OSError:
        eel.start(
            page,
            mode="edge",
            host="localhost",
            close_callback=close_callback,
            port=port,
            disable_cache=True,
        ),

    except Exception:
        mylogging.traceback("Py side terminated...")


def expose(callback_function):
    """Wrap eel expose with try catch block and adding exception callback function
    (for printing error to frontend usually).

    Args:
        callback_function (function): Function that will be called if exposed function fails on some error.
    """

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", module="EelForkExcludeFiles", category=ResourceWarning)

        import EelForkExcludeFiles as eel

    def inner(*args, **kargs):
        try:
            return callback_function(*args, **kargs)

        except Exception:
            if expose_error_callback:
                expose_error_callback()
            else:
                mylogging.traceback(f"Unexpected error in function `{callback_function.__name__}`")

    eel._expose(callback_function.__name__, inner)


def to_vue_plotly(data, names=None):
    """Takes data (dataframe or numpy array) and transforms it to form, that vue-plotly understand.

    Links to vue-plotly:

    https://www.npmjs.com/package/vue-plotly
    https://www.npmjs.com/package/@rleys/vue-plotly  - fork for vue 3 version

    Note:
        In js, you still need to edit the function, it's because no need to have all x axis for every column.
        Download the js function from project-starter and check for example.

    Args:
        data ((np.array, pd.DataFrame)): Plotted data.
        names (list, optional): If using array, you can define names. Defaults to None.

    Returns:
        dict: Data in form for plotting in frontend.
    """

    import pandas as pd
    import numpy as np

    if isinstance(data, (np.ndarray, np.generic)):
        data = pd.DataFrame(data, columns=names)

    data = pd.DataFrame(data)

    numeric_data = data.select_dtypes(include="number").round(decimals=3)
    numeric_data = numeric_data.where(np.isfinite(numeric_data), None)
    # numeric_data = add_none_to_gaps(numeric_data)

    return {
        "x_axis": numeric_data.index.to_list(),
        "y_axis": numeric_data.values.T.tolist(),
        "names": numeric_data.columns.values.tolist(),
    }


def to_table(df, index=False):
    """Takes data (dataframe or numpy array) and transforms it to form, that vue-plotly library understands.

    Args:
        df (pd.DataFrame): Data.
        index (bool): Whether use index as first column (or not at all).

    Returns:
        dict: DatPa in form for creating table in Vuetify v-data-table.
    """
    import pandas as pd
    import numpy as np

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            mylogging.return_str(
                "Only dataframe is allowed in to_table function. If you have Series, "
                "convert it to dataframe. You can use shape (1, x) for one row or use "
                "df.T and shape (x, 1) for one column."
            )
        )

    data = df.copy()
    data = data.round(decimals=3)

    if index:
        data.reset_index(inplace=True)

    # Numpy nan cannot be send to json - replace with None
    data = data.where(~data.isin([np.nan, np.inf, -np.inf]), None)

    headers = [{"text": i, "value": i, "sortable": True} for i in data.columns]

    return {"table": data.to_dict("records"), "headers": headers}
