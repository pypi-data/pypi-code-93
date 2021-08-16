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
__date__ = "04/03/2019"


import os
import copy
import logging

_logger = logging.getLogger(__name__)
try:
    from nabu.app.local_reconstruction import LocalReconstruction
except ImportError as e:
    _logger.error(e)
    has_nabu = False
else:
    has_nabu = True
try:
    from contextlib import AbstractContextManager
except ImportError:
    from tomwer.third_party.contextlib import AbstractContextManager
from silx.utils.enum import Enum as _Enum
from tomwer.core.scan.scanbase import _TomwerBaseDock
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.process.baseprocess import SingleProcess, _input_desc, _output_desc
from nabu.resources.dataset_analyzer import EDFDatasetAnalyzer, HDF5DatasetAnalyzer
from nabu.resources.dataset_analyzer import DatasetAnalyzer
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.utils import docstring
from tomwer.core.process.reconstruction.nabu.utils import check_sinogram_half
from typing import Union
from nabu.io.config import generate_nabu_configfile
from nabu import version as nabu_version
from silx.io.dictdump import h5todict
from . import utils
from . import settings as nabu_settings
from tomoscan.io import HDF5File
from tomwer.core.scan.edfscan import EDFTomoScan
import subprocess
from silx.io.utils import h5py_read_dataset
from nabu.io.config import _extract_nabuconfig_keyvals
from tomwer.core.process.baseprocess import BaseProcess
from tomwer.io.utils.h5pyutils import EntryReader


def run_slices_reconstruction(
    scan: TomwerScanBase,
    config: dict,
    dry_run: bool = False,
    local: bool = True,
    advancement=None,
) -> tuple:
    """
    call nabu for a reconstruction on scan with the given configuration

    :param TomwerScanBase scan: scan to reconstruct
    :param dict config: configuration to run the reconstruction
    :param bool dry_run: do we want to run dry
    :param bool local: do we want to run a local reconstruction
    :param stderr: file to redirect stderr
    :param stdout: file to redirect stdout
    :param advancement: optional Progress class to display advancement
    """
    check_sinogram_half(scan)
    _logger.info("start reconstruction of {}".format(str(scan)))
    # if scan contains some center of position copy it to nabu
    if scan.axis_params is not None and scan.axis_params.relative_cor_value is not None:
        if "reconstruction" in config:
            # move the cor value to the nabu reference
            cor_nabu_ref = scan.axis_params.relative_cor_value + scan.dim_1 / 2.0
            config["reconstruction"]["rotation_axis_position"] = str(cor_nabu_ref)
    _logger.info("set nabu reconstruction parameters to {}".format(str(scan)))
    scan.nabu_recons_params = config

    nabu_configurations = interpret_tomwer_configuration(config, scan=scan)
    db_list = utils.retrieve_lst_of_value_from_str(
        config["phase"]["delta_beta"], type_=float
    )
    ask_sinogram_registration = len(db_list) > 0
    ask_sinogram_load = False
    output_urls = []
    stderrs = []
    stdouts = []
    final_configs = []
    all_succeed = True
    if advancement is not None:
        advancement.setMaxAdvancement(len(nabu_configurations))
    for nabu_configuration in nabu_configurations:
        l_config, slice_index = nabu_configuration
        succeed, urls, stdout, stderr, f_config = run_single_slice_reconstruction(
            config=l_config,
            scan=scan,
            local=local,
            slice_index=slice_index,
            dry_run=dry_run,
            ask_sinogram_registration=ask_sinogram_registration,
            ask_sinogram_load=ask_sinogram_load,
        )
        if slice_index is None:
            continue
        output_urls.extend(urls)
        # if slice_index is None this mean that we are simply creating the
        # .cfg file for nabu full volume.
        stderrs.append(stderr)
        stdouts.append(stdout)
        final_configs.append(f_config)
        all_succeed = all_succeed and succeed
        if ask_sinogram_registration:
            ask_sinogram_load = True
            ask_sinogram_registration = False
        if advancement is not None:
            advancement.increaseAdvancement(1)
    # tag latest reconstructions
    scan.set_latest_reconstructions(output_urls)
    return all_succeed, stdouts, stderrs, final_configs


class NabuSlices(SingleProcess):
    """Definition of the nabu reconstruction Single process"""

    inputs = [
        _input_desc(
            name="change recons params",
            type=_TomwerBaseDock,
            handler="updateReconsParam",
            doc="input with scan + reconstruction parameters",
        ),
        _input_desc(
            name="data", type=TomwerScanBase, handler="pathReceived", doc="scan path"
        ),
    ]
    # Note : scanReady don't intend to find an 'octave_FT_params.h5' file at
    # the folder level.
    # But updateReconsParam should always have a .h5 file defined
    outputs = [_output_desc(name="data", type=TomwerScanBase, doc="scan path")]

    def __init__(self, *arg, **kwargs):
        SingleProcess.__init__(self, *arg, **kwargs)
        self._dry_run = False

    def process(self, scan=None):
        if scan is None:
            return None
        if isinstance(scan, TomwerScanBase):
            scan = scan
        elif isinstance(scan, dict):
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            raise ValueError(
                "input type of {}: {} is not managed" "".format(scan, type(scan))
            )

        run_slices_reconstruction(
            scan=scan, config=self.get_configuration(), dry_run=self.dry_run
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

    def pathReceived(self, scan):
        return self.process(scan=scan)

    @staticmethod
    def program_name():
        return "nabu-slices"

    @staticmethod
    def program_version():
        return nabu_version

    def set_dry_run(self, dry_run):
        self._dry_run = dry_run

    @property
    def dry_run(self):
        return self._dry_run

    @staticmethod
    def get_process_frm_process_file(process_file, entry):
        """
        Read informations regarding the nabu process save in the
        tomwer_process.h5 file

        :param process_file:
        :param entry:
        :return: dictionary with the contain of the nabu process
        :rtype:dict
        """
        if entry is None:
            with HDF5File(process_file, "r", swmr=True) as h5f:
                entries = NabuSlices._get_process_nodes(
                    root_node=h5f, process=NabuSlices
                )
                if len(entries) == 0:
                    _logger.info("unable to find a Axis process in %s" % process_file)
                    return None
                elif len(entries) > 1:
                    raise ValueError("several entry found, entry should be " "specify")
                else:
                    entry = list(entries.keys())[0]
                    _logger.info("take %s as default entry" % entry)

        configuration_path = None
        res = {}

        with HDF5File(process_file, "r", swmr=True) as h5f:
            nabu_nodes = NabuSlices._get_process_nodes(
                root_node=h5f[entry], process=NabuSlices
            )
            index_to_path = {}
            for key, index in nabu_nodes.items():
                index_to_path[index] = key

            if len(nabu_nodes) == 0:
                return None
            # take the last processed dark ref
            last_process_index = sorted(list(nabu_nodes.values()))[-1]
            last_process_dark = index_to_path[last_process_index]
            if (len(index_to_path)) > 1:
                _logger.debug(
                    "several processing found for dark-ref, "
                    "take the last one: %s" % last_process_dark
                )

            for key_name in (
                "class_instance",
                "date",
                "program",
                "sequence_index",
                "version",
            ):
                if key_name in h5f[last_process_dark]:
                    res[key_name] = h5py_read_dataset(h5f[last_process_dark][key_name])
            if "configuration" in h5f[last_process_dark]:
                configuration_path = "/".join(
                    (h5f[last_process_dark].name, "configuration")
                )

        if configuration_path is not None:
            res["configuration"] = h5todict(
                h5file=process_file, path=configuration_path
            )
        return res

    @staticmethod
    def retrieve_last_relative_cor(scan):
        with EntryReader(scan.process_file_url) as h5f:
            latest_nabu_node = BaseProcess.get_most_recent_process(h5f, NabuSlices)
            path = "configuration/reconstruction/rotation_axis_position"
            if path in latest_nabu_node:
                return h5py_read_dataset(latest_nabu_node[path])


def interpret_tomwer_configuration(
    config: dict, scan: Union[TomwerScanBase, None]
) -> tuple:
    """
    tomwer can 'mock' the nabu reconstruction to request more feature.
    Typical use case is that we can ask for reconstruction of several
    slices and not only the volume

    :param dict config: tomwer configuration for nabu
    :param scan: requested if we want to get slices
    :return: tuple of tuples (nabu configuration, is slice)
    """

    def get_nabu_config(config):
        nabu_config = copy.deepcopy(config)
        if "tomwer_slices" in nabu_config:
            del nabu_config["tomwer_slices"]
        return nabu_config

    if "tomwer_slices" in config and scan is not None:
        slices = list(NabuSliceMode.getSlices(config["tomwer_slices"], scan))
    else:
        slices = []

    if "phase" in config and "delta_beta" in config["phase"]:
        pag_dbs = utils.retrieve_lst_of_value_from_str(
            config["phase"]["delta_beta"], type_=float
        )
        if len(pag_dbs) == 0:
            pag_dbs = (None,)
    else:
        pag_dbs = (None,)

    # by default add the slice 'None' which is the slice for the volume
    slices.append(None)
    nabu_config = get_nabu_config(config=config)
    res = []
    for slice_ in slices:
        for pag_db in pag_dbs:
            local_config = copy.deepcopy(nabu_config)
            if pag_db is not None:
                local_config["phase"]["delta_beta"] = str(pag_db)
            res.append((local_config, slice_))
    return tuple(res)


def _get_file_basename_reconstruction(scan, slice_index, pag, db):
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
    if slice_index is None:
        if pag:
            return "_".join((basename + "pag", "db" + str(db).zfill(4)))
        else:
            return basename
    else:
        if pag:
            return "_".join(
                (
                    basename + "slice_pag",
                    str(slice_index).zfill(4),
                    "db" + str(db).zfill(4),
                )
            )
        else:
            return "_".join((basename + "slice", str(slice_index).zfill(4)))


def run_single_slice_reconstruction(
    scan,
    config,
    dry_run,
    slice_index: Union[int, str, None],
    local,
    ask_sinogram_registration: bool,
    ask_sinogram_load: bool,
) -> tuple:
    """
    # TODO: might need something like a context or an option "keep" slice in memory

    :param scan:
    :param config:
    :param dry_run:
    :param Union[None,int, str] slice_index: slice index to reconstruct.
                                             If str should be "middle"
    :param local:
    :param stdout: file to redirect stdout
    :param stderr: file to redirect stderr
    :param bool ask_sinogram_registration: should we ask nabu to register sinogram
    :param bool ask_sinogram_load: should we ask nabu to load sinogram
    :return: (list of output urls, process.stdout, process.stderr)
    """
    if isinstance(slice_index, str):
        if slice_index == "middle":
            slice_index = scan.dim_2 // 2
        else:
            raise ValueError(
                "slice index is expected to an int or 'middle' "
                "and not {}".format(type(slice_index))
            )
    elif not isinstance(slice_index, (int, type(None))):
        raise TypeError(
            "slice index is expected to an int or 'middle' or None"
            "and not {}".format(type(slice_index))
        )
    config_complete = _extract_nabuconfig_keyvals()
    config_complete["dataset"] = scan.get_nabu_dataset_info()
    for key in config_complete.keys():
        if key in config:
            config_complete[key].update(config[key])
    config = config_complete

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
    # handle nabu sinogram step
    if scan.process_file is not None:
        steps_file_basename, _ = os.path.splitext(scan.process_file)
        steps_file_basename = "_".join(
            ("steps_file_basename", "nabu", "sinogram", "save", "step")
        )
        steps_file_basename = steps_file_basename + ".hdf5"
        steps_file = os.path.join(
            os.path.dirname(scan.process_file), steps_file_basename
        )
    else:
        steps_file = ""

    config["output"].update({"overwrite_results": 1})
    config["pipeline"] = {
        "save_steps": "sinogram" if ask_sinogram_registration else "",
        "resume_from_step": "sinogram" if ask_sinogram_load else "",
        "steps_file": steps_file,
    }

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
            _config["output"]["file_prefix"] = _file_name
            if _config["output"]["location"] not in ("", None):
                # if user specify the location
                if not os.path.isdir(_config["output"]["location"]):
                    os.makedirs(_config["output"]["location"])
            else:
                # otherwise default location will be the data root level
                _config["output"]["location"] = scan.path
        return _config

    config = treateOutputConfig(config)
    # the policy is to save nabu .cfg file at the same location as the
    # force overwrite results
    if slice_index is not None:
        config["reconstruction"]["start_z"] = slice_index
        config["reconstruction"]["end_z"] = slice_index
    cfg_folder = os.path.join(
        config["output"]["location"], nabu_settings.NABU_CFG_FILE_FOLDER
    )
    if not os.path.exists(cfg_folder):
        os.makedirs(cfg_folder)

    name = config["output"]["file_prefix"] + nabu_settings.NABU_CONFIG_FILE_EXTENSION
    if not isinstance(scan, EDFTomoScan):
        name = "_".join((scan.entry, name))
    conf_file = os.path.join(cfg_folder, name)
    _logger.info("{}: create {}".format(scan, conf_file))
    # add some tomwer metadata and save the configuration
    # note: for now the section is ignored by nabu but shouldn't stay that way
    with utils.TomwerInfo(config) as config_to_dump:
        generate_nabu_configfile(
            fname=conf_file, config=config_to_dump, options_level="advanced"
        )

    if slice_index is not None and dry_run is False and local:
        if not has_nabu:
            raise ImportError("Fail to import nabu")
        _logger.info(
            "run nabu slice reconstruction for %s with %s" "" % (scan.path, config)
        )
        file_format = config_to_dump["output"]["file_format"]
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
            start_z=None,
            end_z=None,
        )

        return (
            len(recons_urls) > 0,
            recons_urls,
            outs,
            errs,
            config_to_dump,
        )
    else:
        return (True, [], None, None, None)


def get_nabu_dataset_analyzer(scan: TomwerScanBase) -> DatasetAnalyzer:
    """

    :param scan:
    :return:
    """
    if isinstance(scan, EDFTomoScan):
        return EDFDatasetAnalyzer(location=scan.path)
    elif isinstance(scan, HDF5TomoScan):
        assert os.path.exists(scan.master_file)
        assert os.path.isfile(scan.master_file)
        return HDF5DatasetAnalyzer(location=scan.master_file)
    else:
        raise TypeError("given scan type %s is not managed" % type(scan))


class NabuSliceMode(_Enum):
    MIDDLE = "middle"
    OTHER = "other"

    @staticmethod
    def getSlices(slices, scan) -> tuple:
        res = []
        try:
            mode = NabuSliceMode.from_value(slices)
        except ValueError:
            try:
                res = utils.retrieve_lst_of_value_from_str(slices, type_=int)
            except Exception:
                pass
        else:
            if mode == mode.MIDDLE:
                n_slice = scan.dim_2 or 2048
                res.append(n_slice // 2)
            else:
                raise ValueError(
                    "there should be only two ways of defining "
                    "slices: middle one or other, by giving "
                    "an unique value or a list or a tuple"
                )
        return tuple(res)
