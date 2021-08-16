# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility
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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "04/08/2020"


import logging

_logger = logging.getLogger(__name__)
try:
    from nabu.app.local_reconstruction import LocalReconstruction
except ImportError as e:
    _logger.error(e)
    has_nabu = False
else:
    has_nabu = True
from tomwer.core.process.baseprocess import SingleProcess
from tomwer.core.process.baseprocess import _input_desc, _output_desc
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.process.reconstruction.nabu.utils import check_sinogram_half
from . import utils
from . import settings
from nabu.io.config import generate_nabu_configfile
from nabu import version as nabu_version
from tomwer.core.scan.edfscan import EDFTomoScan
import subprocess
from tomwer.utils import docstring
import copy
import os
from tomwer.core.process.baseprocess import BaseProcess
from tomwer.io.utils.h5pyutils import EntryReader
from silx.io.utils import h5py_read_dataset


def run_volume_reconstruction(
    scan: TomwerScanBase,
    config: dict,
    dry_run: bool,
    local: bool,
) -> tuple:

    if scan.nabu_recons_params in ({}, None):
        raise ValueError(
            "no configuration provided. You should run a "
            "reconstruction from nabuslices first."
        )
    check_sinogram_half(scan)
    config_volume = copy.copy(config)
    config_nabu_slices = copy.deepcopy(scan.nabu_recons_params)
    if "tomwer_slices" in config_nabu_slices:
        del config_nabu_slices["tomwer_slices"]

    if "phase" in config_nabu_slices and "delta_beta" in config_nabu_slices["phase"]:
        pag_dbs = utils.retrieve_lst_of_value_from_str(
            config_nabu_slices["phase"]["delta_beta"], type_=float
        )
        if len(pag_dbs) > 1:
            raise ValueError(
                "Several value of delta / beta found for volume reconstruction"
            )

    succeed, output_url, stdouts, stderrs, configs = _run_volume_reconstruction(
        scan=scan,
        config_volume=config_volume,
        config_slices=config_nabu_slices,
        dry_run=dry_run,
        local=local,
    )
    # tag latest reconstructions
    if output_url is not None:
        scan.set_latest_vol_reconstructions(output_url)
    return succeed, stdouts, stderrs, configs


def _run_volume_reconstruction(
    scan: TomwerScanBase,
    config_volume: dict,
    config_slices: dict,
    dry_run: bool,
    local: bool,
) -> tuple:
    dataset_params = scan.get_nabu_dataset_info()
    if "dataset" in config_slices:
        dataset_params.update(config_slices["dataset"])
    config_slices["dataset"] = dataset_params

    if local is True:
        resources_method = "local"
    else:
        resources_method = "slurm"
    config_slices["resources"] = utils.get_nabu_resources_desc(
        scan=scan, workers=1, method=resources_method
    )

    def treateOutputConfig(config_s, config_v) -> tuple:
        """

        :return: (nabu config dict, nabu extra options)
        """
        config_s = copy.deepcopy(config_s)
        pag = False
        db = None
        if "phase" in config_s:
            if "method" in config_s["phase"] and config_s["phase"]["method"] != "":
                pag = True
                if "delta_beta" in config_s["phase"]:
                    db = round(float(config_s["phase"]["delta_beta"]))
        file_name = _get_file_basename_reconstruction(scan=scan, pag=pag, db=db)

        if "output" in config_s:
            config_s["output"]["file_prefix"] = file_name
            if config_s["output"]["location"] not in ("", None):
                # if user specify the location
                if not os.path.isdir(config_s["output"]["location"]):
                    os.makedirs(config_s["output"]["location"])
            else:
                # otherwise default location will be the data root level
                config_s["output"]["location"] = scan.path
            print("has an output folder", config_s["output"]["location"])
        else:
            print("no output folder")

        if "postproc" in config_v:
            config_s["postproc"] = config_v["postproc"]

        extra_opts = config_v
        if "start_z" in extra_opts:
            config_s["reconstruction"]["start_z"] = extra_opts["start_z"]
            del extra_opts["start_z"]
        if "end_z" in extra_opts:
            config_s["reconstruction"]["end_z"] = extra_opts["end_z"]
            del extra_opts["end_z"]

        return config_s, extra_opts

    # force overwrite results
    if "output" not in config_slices:
        config_slices["output"] = {}
    config_slices, extra_opts = treateOutputConfig(config_slices, config_volume)
    config_slices["output"].update({"overwrite_results": 1})

    cfg_folder = os.path.join(
        config_slices["output"]["location"], settings.NABU_CFG_FILE_FOLDER
    )
    if not os.path.exists(cfg_folder):
        os.makedirs(cfg_folder)

    name = config_slices["output"]["file_prefix"] + settings.NABU_CONFIG_FILE_EXTENSION
    if not isinstance(scan, EDFTomoScan):
        name = "_".join((scan.entry, name))
    conf_file = os.path.join(cfg_folder, name)
    _logger.info("{}: create {}".format(scan, conf_file))

    # add some tomwer metadata and save the configuration
    # note: for now the section is ignored by nabu but shouldn't stay that way
    with utils.TomwerInfo(config_slices) as config_to_dump:
        generate_nabu_configfile(
            fname=conf_file, config=config_to_dump, options_level="advanced"
        )
    if dry_run is False and local:
        if not has_nabu:
            raise ImportError("Fail to import nabu")
        _logger.info(
            "run nabu volume reconstruction for {} with {}"
            "".format(str(scan), config_slices)
        )
        # enforce file format to be hdf5
        file_format = config_slices["output"]["file_format"]
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
        outs, errs = process.communicate()

        recons_urls = utils.get_recons_urls(
            file_prefix=config_to_dump["output"]["file_prefix"],
            location=config_to_dump["output"]["location"],
            slice_index=None,
            scan=scan,
            file_format=file_format,
            start_z=config_to_dump["reconstruction"]["start_z"],
            end_z=config_to_dump["reconstruction"]["end_z"],
        )

        return (
            len(recons_urls) > 0,
            recons_urls,
            [
                outs,
            ],
            [
                errs,
            ],
            [
                config_slices,
            ],
        )
    else:
        return (True, [], None, None, None)


def _get_file_basename_reconstruction(scan, pag, db):
    """

    :param TomwerScanBase scan: scan reconstructed
    :param Union[None, int] slice_index: index of the slice reconstructed.
                                         if None, we want to reconstruct the
                                         entire volume
    :param bool pag: is it a paganin reconstruction
    :param int db: delta / beta parameter
    :return: basename of the file reconstructed (without any extension)
    """
    assert type(db) in (int, type(None))
    if isinstance(scan, HDF5TomoScan):
        basename, _ = os.path.splitext(scan.master_file)
        basename = os.path.basename(basename)
    else:
        basename = os.path.basename(scan.path)
    if pag:
        return "_".join((basename + "pag", "db" + str(db).zfill(4), "vol"))
    else:
        return "_".join((basename, "vol"))


class NabuVolume(SingleProcess):
    inputs = [
        _input_desc(
            name="data", type=TomwerScanBase, handler="pathReceived", doc="scan path"
        )
    ]

    outputs = [_output_desc(name="data", type=TomwerScanBase, doc="scan path")]

    def __init__(self, *arg, **kwargs):
        SingleProcess.__init__(self, *arg, **kwargs)
        self._dry_run = False

    def process(self, scan):
        if scan is None:
            return None
        if isinstance(scan, TomwerScanBase):
            scan = scan
        elif isinstance(scan, dict):
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            raise ValueError("input type {} is not managed".format(scan))

        if scan.nabu_recons_params is None:
            raise ValueError(
                "scan need to have reconstruction parameters "
                'registered. Did you process "Nabu slices" '
                "already ?"
            )

        f_stderr = None
        f_stdout = None

        run_volume_reconstruction(
            scan=scan,
            config=self.get_configuration(),
            dry_run=self.dry_run,
            local=True,
            stderr=f_stderr,
            stdout=f_stdout,
        )
        # register result
        entry = "entry"
        if isinstance(scan, HDF5TomoScan):
            entry = scan.entry
        with scan.acquire_process_file_lock():
            self.register_process(
                process_file=scan.process_file,
                entry=entry,
                configuration=self.get_configuration(),
                results={},
                process_index=scan.pop_process_index(),
                overwrite=True,
            )
        return scan

    @docstring(SingleProcess)
    def set_properties(self, properties):
        self.set_configuration(configuration=properties["_rpSetting"])

    def set_configuration(self, configuration: dict) -> None:
        SingleProcess.set_configuration(self, configuration=configuration)
        if "dry_run" in configuration:
            self.set_dry_run(bool(configuration["dry_run"]))

    @staticmethod
    def program_name():
        return "nabu-volume"

    @staticmethod
    def program_version():
        return nabu_version

    def set_dry_run(self, dry_run):
        self._dry_run = dry_run

    @property
    def dry_run(self):
        return self._dry_run

    def pathReceived(self, scan):
        return self.process(scan=scan)

    @staticmethod
    def retrieve_last_relative_cor(scan):
        with EntryReader(scan.process_file_url) as h5f:
            latest_nabu_node = BaseProcess.get_most_recent_process(h5f, NabuVolume)
            path = "configuration/reconstruction/rotation_axis_position"
            if path in latest_nabu_node:
                return h5py_read_dataset(latest_nabu_node[path])
