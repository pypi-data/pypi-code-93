# coding: utf-8
###########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
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
#############################################################################

"""contain utils for score process
"""

__authors__ = [
    "H.Payno",
]
__license__ = "MIT"
__date__ = "12/05/2021"


try:
    from nabu.app.local_reconstruction import LocalReconstruction
except ImportError as e:
    has_nabu = False
else:
    has_nabu = True
from typing import Union
from tomwer.core.scan.edfscan import EDFTomoScan
from ..nabu import settings as nabu_settings
from tomwer.core.process.reconstruction.nabu.nabuslices import (
    _get_file_basename_reconstruction,
    generate_nabu_configfile,
)
import subprocess
from tomwer.io.utils import format_stderr_stdout
from . import utils
import logging
import os


_logger = logging.getLogger(__name__)


def run_nabu_one_slice_several_config(
    scan,
    nabu_configs,
    dry_run,
    slice_index: Union[int, str],
    local,
    file_format,
    advancement=None,
) -> tuple:
    """
    # TODO: might need something like a context or an option "keep" slice in memory

    :param scan:
    :param nabu_configs: list of nabu configurations to be run
    :param dry_run:
    :param int slice_index: slice index to reconstruct or "middle"
    :param local:
    :param advancement: optional Progress class to display advancement
    :return: tuple with (success, recons_urls (list of output urls),
             tuple of outs, tuples of errs)
    """
    if slice_index == "middle":
        if scan.dim_2 is not None:
            slice_index = scan.dim_2 // 2
        else:
            _logger.warning(
                "scan.dim_2 returns None, unable to deduce middle " "pick 1024"
            )
            slice_index = 1024
    assert isinstance(slice_index, int), "slice_index should be an int"

    def preprocess_config(config, cor: float):
        dataset_params = scan.get_nabu_dataset_info()
        if "dataset" in config:
            dataset_params.update(config["dataset"])
        config["dataset"] = dataset_params

        if local is True:
            resources_method = "local"
        else:
            resources_method = "slurm"
        config["resources"] = utils.get_nabu_resources_desc(
            scan=scan, workers=1, method=resources_method
        )
        # force overwrite results
        if "output" not in config:
            config["output"] = {}
        config["output"].update({"overwrite_results": 1})

        def treateOutputConfig(_config):
            """
            - add or overwrite some parameters of the dictionary
            - create the output directory if does not exist
            """
            pag = False
            db = None
            if "phase" in _config:
                if "method" in _config["phase"] and _config["phase"]["method"] != "":
                    pag = True
                    if "delta_beta" in _config["phase"]:
                        db = round(float(_config["phase"]["delta_beta"]))
            if "output" in config:
                _file_name = _get_file_basename_reconstruction(
                    scan=scan, slice_index=slice_index, pag=pag, db=db
                )
                _config["output"]["file_prefix"] = "cor_{}_{}".format(_file_name, cor)
                if _config["output"]["location"] not in ("", None):
                    # if user specify the location
                    if not os.path.isdir(_config["output"]["location"]):
                        os.makedirs(_config["output"]["location"])
                else:
                    # otherwise default location will be the data root level
                    _config["output"]["location"] = os.sep.join(
                        scan.path, "saaxis_results"
                    )
            if "reconstruction" not in _config:
                _config["reconstruction"] = {}
            _config["reconstruction"]["start_z"] = slice_index
            _config["reconstruction"]["end_z"] = slice_index
            return _config

        config = treateOutputConfig(config)
        # the policy is to save nabu .cfg file at the same location as the
        # force overwrite results

        cfg_folder = os.path.join(
            config["output"]["location"],
            nabu_settings.NABU_CFG_FILE_FOLDER,
        )
        if not os.path.exists(cfg_folder):
            os.makedirs(cfg_folder)

        name = (
            config["output"]["file_prefix"] + nabu_settings.NABU_CONFIG_FILE_EXTENSION
        )
        if not isinstance(scan, EDFTomoScan):
            name = "_".join((scan.entry, name))
        conf_file = os.path.join(cfg_folder, "cor_{}_{}".format(cor, name))
        return config, conf_file

    recons_urls = {}
    outs = []
    errs = []
    if advancement:
        advancement.setMaxAdvancement(len(nabu_configs))
    # TODO: add logger and extra options
    for cor, config in nabu_configs.items():
        config, conf_file = preprocess_config(config, cor)
        # add some tomwer metadata and save the configuration
        # note: for now the section is ignored by nabu but shouldn't stay that way
        with utils.TomwerInfo(config) as config_to_dump:
            generate_nabu_configfile(
                fname=conf_file, config=config_to_dump, options_level="advanced"
            )
        if dry_run:
            continue

        if slice_index is not None and dry_run is False and local:
            if not has_nabu:
                raise ImportError("Fail to import nabu")
            _logger.info(
                "run nabu slice reconstruction for %s with %s" "" % (scan.path, config)
            )

            # need to be executed in his own context
            command = " ".join(
                ("python", "-m", "nabu.resources.cli.reconstruct", conf_file)
            )
            _logger.info('call nabu from "{}"'.format(command))

            process = subprocess.Popen(
                command,
                shell=True,
                cwd=scan.path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            out, err = process.communicate()
            out_str = format_stderr_stdout(out, err)
            outs.append(out)
            errs.append(err)

        urls = utils.get_recons_urls(
            file_prefix=config_to_dump["output"]["file_prefix"],
            location=config_to_dump["output"]["location"],
            slice_index=None,
            scan=scan,
            file_format=file_format,
            start_z=None,
            end_z=None,
        )
        # specific treatment for cor: rename output files
        recons_urls[cor] = urls
        if advancement:
            advancement.increaseAdvancement(1)
    return (
        len(recons_urls) > 0,
        recons_urls,
        tuple(outs),
        tuple(errs),
    )
