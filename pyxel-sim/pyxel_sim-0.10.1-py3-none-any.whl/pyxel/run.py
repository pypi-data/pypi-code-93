#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel detector simulation framework.

Pyxel is a detector simulation framework, that can simulate a variety of
detector effects (e.g., cosmic rays, radiation-induced CTI in CCDs, persistence
in MCT, charge diffusion, crosshatches, noises, crosstalk etc.) on a given image.
"""
import argparse
import logging
import os
import shutil
import sys
import time
import typing as t
from pathlib import Path

import dask
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import pyplot as plt

from pyxel import __version__ as version
from pyxel import inputs_outputs as io
from pyxel.calibration import Calibration, CalibrationResult
from pyxel.configuration import Configuration, load, save
from pyxel.detectors import CCD, CMOS
from pyxel.dynamic import Dynamic  # , DynamicResult
from pyxel.parametric import Parametric, ParametricResult
from pyxel.pipelines import DetectionPipeline, Processor
from pyxel.single import Single
from pyxel.util import download_examples

# from tqdm.notebook import tqdm


if t.TYPE_CHECKING:
    from .inputs_outputs import (
        CalibrationOutputs,
        DynamicOutputs,
        ParametricOutputs,
        SingleOutputs,
    )


def single_mode(
    single: "Single",
    detector: t.Union["CCD", "CMOS"],
    pipeline: "DetectionPipeline",
) -> None:
    """Run a 'single' pipeline.

    Parameters
    ----------
    single
    detector
    pipeline

    Returns
    -------
    None
    """
    logging.info("Mode: Single")

    single_outputs = single.outputs  # type: SingleOutputs
    # detector.set_output_dir(single_outputs.output_dir)  # TODO: Remove this

    processor = Processor(detector=detector, pipeline=pipeline)

    _ = processor.run_pipeline()

    single_outputs.save_to_file(processor)
    # single_outputs.single_to_plot(processor)


def parametric_mode(
    parametric: "Parametric",
    detector: t.Union["CCD", "CMOS"],
    pipeline: "DetectionPipeline",
    with_dask: bool = False,
) -> "ParametricResult":
    """Run a 'parametric' pipeline.

    Parameters
    ----------
    parametric: Parametric
    detector: Detector
    pipeline: Pipeline
    with_dask: bool

    Returns
    -------
    result: ParametricResult
    """
    logging.info("Mode: Parametric")

    parametric_outputs = parametric.outputs  # type: ParametricOutputs
    detector.set_output_dir(parametric_outputs.output_dir)  # TODO: Remove this

    # TODO: This should be done during initializing of object `Configuration`
    # parametric_outputs.params_func(parametric)

    processor = Processor(detector=detector, pipeline=pipeline)

    result = parametric.run_parametric(processor=processor)

    if parametric_outputs.save_parametric_data:
        parametric_outputs.save_parametric_datasets(
            result=result, mode=parametric.parametric_mode
        )

    return result


def dynamic_mode(
    dynamic: "Dynamic",
    detector: t.Union["CCD", "CMOS"],
    pipeline: "DetectionPipeline",
) -> xr.Dataset:
    """Run a 'dynamic' pipeline.

    Parameters
    ----------
    dynamic
    detector
    pipeline

    Returns
    -------
    None
    """

    logging.info("Mode: Dynamic")

    dynamic_outputs = dynamic.outputs  # type: DynamicOutputs

    detector.set_output_dir(dynamic_outputs.output_dir)  # TODO: Remove this

    processor = Processor(detector=detector, pipeline=pipeline)

    result = dynamic.run_dynamic(processor=processor)

    if dynamic_outputs.save_dynamic_data:
        dynamic_outputs.save_dynamic_outputs(dataset=result)

    return result


def calibration_mode(
    calibration: "Calibration",
    detector: t.Union["CCD", "CMOS"],
    pipeline: "DetectionPipeline",
    compute_and_save: bool = True,
) -> t.Tuple[xr.Dataset, pd.DataFrame, pd.DataFrame, t.Sequence]:
    """Run a 'calibration' pipeline.

    Parameters
    ----------
    calibration: Calibration
    detector: Detector
    pipeline: DetectionPipeline
    compute_and_save: bool

    Returns
    -------
    tuple
    """
    logging.info("Mode: Calibration")

    calibration_outputs = calibration.outputs  # type: CalibrationOutputs
    detector.set_output_dir(calibration_outputs.output_dir)  # TODO: Remove this

    processor = Processor(detector=detector, pipeline=pipeline)

    ds_results, df_processors, df_all_logs = calibration.run_calibration(
        processor=processor, output_dir=calibration_outputs.output_dir
    )

    # TODO: Save the processors from 'df_processors'
    # TODO: Generate plots from 'ds_results'

    # TODO: Do something with 'df_all_logs' ?

    # TODO: create 'output' object with .calibration_outputs
    # TODO: use 'fitting.get_simulated_data' ==> np.ndarray

    # geometry = processor.detector.geometry
    # calibration.post_processing(
    #     champions=champions,
    #     output=calibration_outputs,
    #     row=geometry.row,
    #     col=geometry.col,
    # )
    filenames = calibration.post_processing(
        ds=ds_results, df_processors=df_processors, output=calibration_outputs
    )

    if compute_and_save:

        computed_ds, df_processors, df_logs, filenames = dask.compute(
            ds_results, df_processors, df_all_logs, filenames
        )

        if calibration_outputs.save_calibration_data:
            calibration_outputs.save_calibration_outputs(
                dataset=computed_ds, logs=df_logs
            )
            print(f"Saved calibration outputs to {calibration_outputs.output_dir}")

        result = CalibrationResult(
            dataset=computed_ds,
            processors=df_processors,
            logs=df_logs,
            filenames=filenames,
        )

    else:
        result = CalibrationResult(
            dataset=ds_results,
            processors=df_processors,
            logs=df_all_logs,
            filenames=filenames,
        )

    return result


def output_directory(configuration: Configuration) -> Path:
    """Return the output directory from the configuration.

    Parameters
    ----------
    configuration

    Returns
    -------
    output_dir
    """
    if isinstance(configuration.single, Single):
        output_dir = configuration.single.outputs.output_dir
    elif isinstance(configuration.calibration, Calibration):
        output_dir = configuration.calibration.outputs.output_dir
    elif isinstance(configuration.dynamic, Dynamic):
        output_dir = configuration.dynamic.outputs.output_dir
    elif isinstance(configuration.parametric, Parametric):
        output_dir = configuration.parametric.outputs.output_dir
    else:
        raise (ValueError("Outputs not initialized."))
    return output_dir


def create_model(newmodel: str) -> None:
    """Create a new module using pyxel/templates/MODELTEMPLATE.py.

    Parameters
    ----------
    newmodel: modeltype/modelname

    Returns
    -------
    None
    """
    try:
        arguments = newmodel.split("/")
        location = f"{arguments[0]}"
        model_name = f"{arguments[1]}"
    except Exception:
        sys.exit(
            f"""
        Can't create model {arguments}, please use location/newmodelname
        as an argument for creating a model
        """
        )

    # Is not working on UNIX AND Windows if I do not use os.path.abspath
    path = os.path.abspath(os.getcwd() + "/pyxel/models/" + location + "/")
    template_string = "_TEMPLATE"
    template_location = "_LOCATION"

    # Copying the template with the user defined model_name instead
    import pyxel

    src = os.path.abspath(os.path.dirname(pyxel.__file__) + "/templates/")
    dest = os.path.abspath(
        os.path.dirname(pyxel.__file__) + "/models/" + location + "/"
    )

    try:
        try:
            os.mkdir(dest)
        except FileExistsError:
            logging.info(f"{dest} already exists, folder not created")
        # Replacing all of template in filenames and directories by model_name
        for dirpath, subdirs, files in os.walk(src):
            for x in files:
                pathtofile = os.path.join(dirpath, x)
                new_pathtofile = os.path.join(
                    dest, x.replace(template_string, model_name)
                )
                shutil.copy(pathtofile, new_pathtofile)
                # Open file in the created copy
                with open(new_pathtofile, "r") as file_tochange:
                    # Replace any mention of template by model_name
                    new_contents = file_tochange.read().replace(
                        template_string, model_name
                    )
                    new_contents = new_contents.replace(template_location, location)
                    new_contents = new_contents.replace("%(date)", time.ctime())
                with open(new_pathtofile, "w+") as file_tochange:
                    file_tochange.write(new_contents)
                # Close the file other we can't rename it
                file_tochange.close()

            for x in subdirs:
                pathtofile = os.path.join(dirpath, x)
                os.mkdir(pathtofile.replace(template_string, model_name))
            logging.info("Module " + model_name + " created.")
        print("Module " + model_name + " created in " + path + ".")
    # Directories are the same
    except shutil.Error as e:
        logging.critical("Error while duplicating " + template_string + ": %s" % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        logging.critical(model_name + " not created. Error: %s" % e)
    return None


def run(input_filename: str, random_seed: t.Optional[int] = None) -> None:
    """TBW.

    Parameters
    ----------
    input_filename
    random_seed
    random_seed
    """
    logging.info("Pyxel version %s", version)
    logging.info("Pipeline started.")

    start_time = time.time()
    if random_seed:
        np.random.seed(random_seed)

    configuration = load(
        Path(input_filename).expanduser().resolve()
    )  # type: Configuration

    output_dir = output_directory(configuration)

    save(input_filename=input_filename, output_dir=output_dir)

    pipeline = configuration.pipeline  # type: DetectionPipeline

    if isinstance(configuration.ccd_detector, CCD):
        detector = configuration.ccd_detector  # type: t.Union[CCD, CMOS]
    elif isinstance(configuration.cmos_detector, CMOS):
        detector = configuration.cmos_detector
    else:
        raise NotImplementedError("Detector is not defined in YAML config. file!")

    if isinstance(configuration.single, Single):
        single = configuration.single  # type: Single
        single_mode(single=single, detector=detector, pipeline=pipeline)

    elif isinstance(configuration.calibration, Calibration):

        calibration = configuration.calibration  # type: Calibration
        _ = calibration_mode(
            calibration=calibration, detector=detector, pipeline=pipeline
        )

    elif isinstance(configuration.parametric, Parametric):
        parametric = configuration.parametric  # type: Parametric
        parametric_mode(parametric=parametric, detector=detector, pipeline=pipeline)

    elif isinstance(configuration.dynamic, Dynamic):

        dynamic = configuration.dynamic  # type: Dynamic
        dynamic_mode(dynamic=dynamic, detector=detector, pipeline=pipeline)

    else:
        raise NotImplementedError("Please provide a valid simulation mode !")

    logging.info("Pipeline completed.")
    logging.info("Running time: %.3f seconds" % (time.time() - start_time))
    # Closing the logger in order to be able to move the file in the output dir
    logging.shutdown()
    io.save_log_file(output_dir)
    plt.close()


# TODO: Use library 'click' instead of 'parser' ? See issue #62
#       Add an option to display colors ? (very optional)
def main() -> None:
    """Define the argument parser and run Pyxel."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__
    )

    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="Increase output verbosity (-v/-vv/-vvv)",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="Pyxel, version {version}".format(version=version),
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Configuration file to load (YAML)",
    )

    parser.add_argument("-s", "--seed", type=int, help="Random seed for the framework")

    parser.add_argument(
        "--download-examples",
        nargs="?",
        const="pyxel-examples",
        help="Install examples to the specified directory, default is /pyxel-examples.",
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force flag for saving the examples.",
    )

    parser.add_argument(
        "-cm",
        "--createmodel",
        type=str,
        help="""Use: -cm arg1/arg2. Create a new module in\
        pyxel/models/arg1/arg2 using a template\
        (pyxel/templates/MODELTEMPLATE.py)""",
    )

    # parser.add_argument('-g', '--gui', default=False, type=bool, help='run Graphical User Interface')
    # parser.add_argument('-p', '--port', default=9999, type=int, help='The port to run the web server on')

    opts = parser.parse_args()

    logging_level = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG][
        min(opts.verbosity, 3)
    ]
    log_format = (
        "%(asctime)s - %(name)s - %(threadName)30s - %(funcName)30s \t %(message)s"
    )
    logging.basicConfig(
        filename="pyxel.log",
        level=logging_level,
        format=log_format,
        datefmt="%d-%m-%Y %H:%M:%S",
    )
    # If user wants the log in stdout AND in file, use the three lines below
    stream_stdout = logging.StreamHandler(sys.stdout)
    stream_stdout.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(stream_stdout)

    if opts.config:
        run(input_filename=opts.config, random_seed=opts.seed)
    elif opts.download_examples:
        download_examples(foldername=opts.download_examples, force=opts.force)
    elif opts.createmodel:
        create_model(newmodel=opts.createmodel)
    else:
        print("Define a YAML configuration file!")


if __name__ == "__main__":
    main()
