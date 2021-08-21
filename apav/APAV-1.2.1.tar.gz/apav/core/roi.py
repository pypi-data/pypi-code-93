"""
This file is part of APAV.

APAV is a python package for performing analysis and visualization on
atom probe tomography data sets.

Copyright (C) 2018 Jesse Smith

APAV is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

APAV is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with APAV.  If not, see <http://www.gnu.org/licenses/>.
"""

from sys import getsizeof
from functools import lru_cache
import os
import struct
from enum import Enum
from warnings import warn

import numpy as n
import numpy.linalg as la

from apav.utils import validate
from apav.utils.helpers import unique_int8, minmax
from apav.core.multipleevent import get_mass_indices
from apav.utils.validate import NoMultiEventError, NoDetectorInfoError, NoTOFError
from apav.core.histogram import histogram1d
from apav.utils.hinting import *
from apav.visualization.factory import vfactory


class Roi:
    """
    High level container for operating on atom probe data sets.
    """
    def __init__(self,
                 xyz: ndarray,
                 mass: ndarray,
                 misc: dict = None):
        """
        This data structure is the entry point for loading or constructing atom probe data set for use with other
        components of APAV. Fictitious atom probe data set can be created by providing the required XYZ and mass/charge
        arrays, or by the alternate constructors for loading from common file types. For example:

        Manual data set::

        >>> xyz = np.array([[1.2, 0.3, 12.6], [-76.2, 45.6, 0.7]])
        >>> mass = np.array([12.4, 6.1, 14.9])
        >>> fake_data = Roi(xyz, mass)

        Load from file::

        >>> pos_data = Roi.from_pos("path_to_pos_file.pos")  # load a pos file
        >>> epos_data = Roi.from_epos("path_to_epos_file.epos")  # load a epos file
        >>> ato_data = Roi.from_ato("path_to_ato_file.ato")  # load a ato file

        :param xyz: xyz atom coordinates
        :param mass: Mass to charge ratios
        :param misc: Dict of other data, (i.e. ions per pulse or detector x pos)
        """
        super().__init__()
        if not isinstance(xyz, ndarray) or not isinstance(mass, ndarray):
            raise TypeError("Mass and xyz coordinates must be numpy arrays")
        if len(xyz.shape) != 2 or xyz.shape[1] != 3:
            raise ValueError(f"XYZ array is not correct shape {xyz.shape} should be (Mx3)")
        if len(mass.shape) != 1:
            print("Mass shape", len(mass.shape))
            raise ValueError("Mass array must be 1 dimensional")
        if xyz.shape[0] != mass.shape[0]:
            raise ValueError("XYZ and mass must have the same number of entries (per atom)")

        self._filepath = ""
        self._xyz = xyz
        self._mass = mass
        self._misc = misc or {}

        # The mask is a 1d array of indices into the raw data (xyz/mass/etc). If the mask is None then
        # we use the whole data set, otherwise accessing any of this data will first slice using this mask.
        # The mask gets set when creating sub-rois from existing (i.e. a cylinder roi).
        self._mask = None

        # Delay computing these values until they called for the first time, greatly increases initialization speed
        # with large data sets. numpy.unique can be slower than reading and initializing the data in certain cases
        self._multiplicities = None
        self._multiplicity_counts = None
        self._xyz_extents = None
        self._dimensions = None

        self._from_pos_or_epos = False

    @property
    def filepath(self) -> str:
        """
        Get the file path, if the :class:`Roi` was loaded from a file
        """
        return self._filepath

    @property
    def multiplicities(self) -> ndarray:
        """
        Get an array of the sorted multiplicities.
        """
        if not self.has_multiplicity_info():
            raise NoMultiEventError()
        elif self.has_multiplicity_info() and self._multiplicities is None:
            self._multiplicities = unique_int8(self.misc["ipp"])
            self._multiplicities.sort()
            self._multiplicities = self._multiplicities[1:]
        return self._multiplicities

    @property
    def xyz(self) -> n.ndarray:
        """
        Get the Mx3 array of the x/y/z positions
        """
        if self._mask is None:
            return self._xyz
        else:
            return self._xyz[self._mask]

    @property
    def mass(self) -> n.ndarray:
        """
        Get the Mx1 array of the mass/charge ratios of each position
        """
        if self._mask is None:
            return self._mass
        else:
            return self._mass[self._mask]

    @property
    def misc(self) -> dict:
        """
        Get the dictionary of miscellaneous data for each position. This is usually populated
        automatically when the :class:`Roi` is create from :meth:`Roi.from_epos` or :meth:`Roi.from_ato`.
        """
        if self._mask is None:
            return self._misc
        else:
            return {key: value[self._mask] for key, value in self._misc.items()}

    @property
    def counts(self) -> float:
        """
        Get the total number of detected ions
        """
        return self.xyz.shape[0]

    @property
    def dimensions(self) -> ndarray:
        """
        Get the x/y/z dimensions of the dataset
        """
        # return tuple(i[1] - i[0] for i in self.xyz_extents)
        return n.diff(self.xyz_extents).ravel()

    @property
    def mass_extents(self) -> Tuple[float, float]:
        """
        Get the min and max detected mass/charge ratio
        """
        return self.mass.min(), self.mass.max()

    @property
    def xyz_extents(self) -> Tuple[Tuple[float, float], ...]:
        """
        Get the min/max spatial values of the x/y/z coordinates in nm.
        """
        if self._xyz_extents is None:
            # The 3 major 64-bit operating systems are little endian, so we must byte swap before using the numba
            # accelerated minmax function if the roi was originally from a pos or epos file (these files are big endian)
            if self._from_pos_or_epos is True:
                self._xyz_extents = tuple(minmax(self.xyz[:, i].byteswap().view(n.float32)) for i in range(self.xyz.shape[1]))
            else:
                self._xyz_extents = tuple(minmax(self.xyz[:, i]) for i in range(self.xyz.shape[1]))
        return self._xyz_extents

    @property
    def xyz_center(self) -> ndarray:
        """
        Get the center of all positions as the mean of all x/y/z values
        """
        return n.mean(self.xyz, axis=0)

    @property
    def detector_extents(self) -> (tuple, tuple):
        """
        Get the min/max spatial values in x/y detector coordinates
        """
        if "det_x" not in self.misc.keys():
            raise NoDetectorInfoError()

        dx = (self.misc["det_x"].min(), self.misc["det_x"].max())
        dy = (self.misc["det_y"].min(), self.misc["det_y"].max())
        return dx, dy

    def has_detailed_info(self) -> bool:
        """
        Get if the Roi has any supplementary information available (other than x/y/z/mass-charge).
        """
        return bool(len(self.misc))

    def has_multiplicity_info(self) -> bool:
        """
        Get if the Roi has multiple detector event information
        """
        return "ipp" in self.misc.keys()

    def has_tof_info(self) -> bool:
        """
        Get if the the Roi has time of flight information
        """
        return "tof" in self.misc.keys()

    @classmethod
    def from_apt(cls, filepath: str, verbose: bool = False):
        """
        Read the contents of an apt file into a Roi container

        :param filepath: Path to apt file
        :param verbose: Print the structure of the apt file as it is read (for debug purposes)
        """

        validate.file_exists(filepath)

        class RelType(Enum):
            REL_UNKNOWN = 0
            ONE_TO_ONE = 1
            INDEXED = 2,
            UNRELATED = 3
            ONE_TO_MANY = 4

        class RecordType(Enum):
            RT_UNKNOWN = 0
            FIXED_SIZE = 1
            VARIABLE_SIZE = 2
            VARIABLE_INDEXED = 3

        class RecordDataType(Enum):
            DT_UNKNOWN = 0
            INT = 1
            UINT = 2
            FLOAT = 3
            CHARSTRING = 4
            OTHER = 5

        class Dtype(Enum):
            int32 = 4
            int64 = 8
            char = 1
            wchar_t = 2
            filetime = 8

        def record_dtype2numpy_dtype(rec_dtype: RecordDataType, size: int):
            """
            Map a section's record data type to its equivalent numpy dtype
            """
            if rec_dtype in (RecordDataType.UINT, RecordDataType.CHARSTRING):
                raise ValueError("Cannot map to UINT or CHARSTRING")

            int_map = {
                8: n.int8,
                16: n.int16,
                32: n.int32,
                64: n.int64
            }

            float_map = {
                32: n.float32,
                64: n.float64
            }

            if rec_dtype == RecordDataType.INT:
                return int_map[size]
            elif rec_dtype == RecordDataType.FLOAT:
                return float_map[size]
            else:
                raise ValueError(f"Unexpected record data type {rec_dtype}")

        # Maps the apt format data type to str format needed for struct.unpack
        dtype2fmt = {
            Dtype.int32: "i",
            Dtype.int64: "q",
            Dtype.char: "c",
            Dtype.filetime: "Q",
            Dtype.wchar_t: "c"
        }

        # Maps the apt format data type to python data type
        dtype2constr = {
            Dtype.int32: int,
            Dtype.int64: int,
            Dtype.char: lambda x: x.decode("utf-8"),
            Dtype.wchar_t: lambda x: x.decode("utf-16"),
            Dtype.filetime: int
        }

        with open(filepath, "rb") as dat:
            def read_chunk(dtype: Dtype,
                           count: int = 1,
                           start: Union[None, int] = None) -> Union[Tuple[Any], Any]:
                if isinstance(start, int):
                    dat.seek(start)

                fmt = dtype2fmt[dtype]*count
                constructor = dtype2constr[dtype]
                dtype_size = dtype.value

                if dtype in (Dtype.wchar_t, Dtype.char):
                    return constructor(dat.read(dtype_size*count)).replace("\x00", "")
                else:
                    retn = struct.unpack("<" + fmt, dat.read(dtype_size * count))

                if len(retn) == 1:
                    return constructor(retn[0])
                else:
                    return tuple(constructor(i) for i in retn)

            cSignature = read_chunk(Dtype.char, 4)

            # Read the APT file header --------------------------------------------------------------------------------
            iHeaderSize = read_chunk(Dtype.int32)
            iHeaderVersion = read_chunk(Dtype.int32)
            wcFileName = read_chunk(Dtype.wchar_t, 256)
            ftCreationTime = read_chunk(Dtype.filetime)
            llIonCount = read_chunk(Dtype.int64)

            if verbose:
                print(f"\nReading header of {filepath}")
                print(f"\tcSignature: " + cSignature)
                print(f"\tiHeaderSize: {iHeaderSize}")
                print(f"\tiHeaderVersion: {iHeaderVersion}")
                print(f"\twcFileName: {wcFileName}")
                print(f"\tftCreationTime: {ftCreationTime}")
                print(f"\t11IonCount: {llIonCount}")

            # Read the APT sections ----------------------------------------------------------------------------
            section_start = iHeaderSize
            section_data = {}

            while True:
                sec_sig = read_chunk(Dtype.char, 4, section_start)

                if sec_sig == '':
                    # EOF reached
                    break

                # Flag used to not include a section in the Roi when a configuration
                # situation is not implemented or handled
                skip_sec = False

                sec_header_size = read_chunk(Dtype.int32)
                sec_header_ver = read_chunk(Dtype.int32)
                sec_type = read_chunk(Dtype.wchar_t, 32)
                sec_ver = read_chunk(Dtype.int32)

                sec_rel_type = RelType(read_chunk(Dtype.int32))
                is_one_to_one = sec_rel_type == RelType.ONE_TO_ONE
                if not is_one_to_one:
                    warn(f"APAV does not handle REL_TYPE != ONE_TO_ONE, section \"{sec_type}\" will be ignored")
                    skip_sec = True

                sec_rec_type = RecordType(read_chunk(Dtype.int32))
                is_fixed_size = sec_rec_type == RecordType.FIXED_SIZE
                if not is_fixed_size:
                    warn(f"APAV does not handle RECORD_TYPE != FIXED_SIZE, section \"{sec_type}\" will be ignored")
                    skip_sec = True

                sec_rec_dtype = RecordDataType(read_chunk(Dtype.int32))
                if sec_rec_dtype in (RecordDataType.DT_UNKNOWN, RecordDataType.OTHER, RecordDataType.CHARSTRING):
                    warn(f"APAV does not handle RECORD_TYPE == {sec_rec_dtype}, section \"{sec_type}\" will be ignored")
                    skip_sec = True

                sec_dtype_size = read_chunk(Dtype.int32)
                sec_rec_size = read_chunk(Dtype.int32)
                sec_data_unit = read_chunk(Dtype.wchar_t, 16)
                sec_rec_count = read_chunk(Dtype.int64)
                sec_byte_count = read_chunk(Dtype.int64)

                if verbose:
                    print("\nReading new section")
                    print(f"\tSection header sig: {sec_sig}")
                    print(f"\tSection header size: {sec_header_size}")
                    print(f"\tSection header version: {sec_header_ver}")
                    print(f"\tSection type: {sec_type}")
                    print(f"\tSection version: {sec_ver}")
                    print(f"\tSection relative type: {sec_rel_type}")
                    print(f"\tSection record type: {sec_rec_type}")
                    print(f"\tSection record data type: {sec_rec_dtype}")
                    print(f"\tSection data type size (bits): {sec_dtype_size}")
                    print(f"\tSection record size: {sec_rec_size}")
                    print(f"\tSection data type unit: {sec_data_unit}")
                    print(f"\tSection record count: {sec_rec_count}")
                    print(f"\tSection byte count: {sec_byte_count}")

                if not skip_sec:
                    columns = int(sec_rec_size/(sec_dtype_size/8))
                    records = int(sec_rec_count)
                    count = records*columns
                    in_data = n.fromfile(filepath,
                                         record_dtype2numpy_dtype(sec_rec_dtype, sec_dtype_size),
                                         count,
                                         offset=section_start+sec_header_size)
                    if columns > 1:
                        section_data[sec_type] = in_data.reshape(records, columns)
                    else:
                        section_data[sec_type] = in_data

                section_start = section_start + sec_byte_count + sec_header_size

        has_mass_data = "Mass" in section_data.keys()
        has_pos_data = "Position" in section_data.keys()

        # Map some APT section names to names that APAV expects, otherwise the provided name is retained
        name_map = {
            "Multiplicity": "ipp",
            "Time of Flight": "tof",
            "XDet_mm": "det_x",
            "YDet_mm": "det_y",
            "Voltage": "dc_voltage",
            "Pulse Voltage": "pulse_voltage"
        }

        # Require mass and position data, clean up some sections, and account for possible duplicate sections (i.e.
        # XDet_mm + YDet_mm combined with Detector Coordinates
        if not has_mass_data:
            raise AttributeError("APT file must have include a mass section")
        elif not has_pos_data:
            raise AttributeError("APT file must have include a position section")

        mass = section_data.pop("Mass")
        pos = section_data.pop("Position")

        # There are 2 difference ways that detector space coordinates can be included in an apt file, as a single
        # section containing both x/y or the x and y in separate sections. Only when the separate x/y sections are not
        # present we will load the combined x/y data (which we separate into different x and y arrays).
        if "Detector Coordinates" in section_data.keys():
            temp = section_data.pop("Detector Coordinates")
            if "XDet_mm" not in section_data.keys():
                section_data["det_x"] = temp[:, 0]
            if "YDet_mm" not in section_data.keys():
                section_data["det_y"] = temp[:, 1]

        roi = cls(pos, mass)
        roi._filepath = filepath
        for key, data in section_data.items():
            name = key if key not in name_map.keys() else name_map[key]
            roi.misc[name] = data

        return roi

    @classmethod
    def from_pos(cls, filepath: str):
        """
        Read the contents of a pos file into a Roi container

        :param filepath: Path to pos file
        """
        validate.file_exists(filepath)

        dtype = n.dtype(">f4")
        data = n.fromfile(filepath, dtype=dtype, sep="")
        data.shape = (int(data.size/4), 4)

        retn = cls(data[:, :3], data[:, 3])
        retn._filepath = filepath
        retn._from_pos_or_epos = True
        return retn

    @classmethod
    def from_epos(cls, filepath: str):
        """
        Read the contents of an extended pos file into an Roi container. Suitable for multiple-hit analysis.

        :param filepath: Path to epos file
        """
        validate.file_exists(filepath)

        f = ">f4"
        i = ">i4"
        dtype = n.dtype([("xyz", (f, 3)),
                         ("mass", f),
                         ("tof", f),
                         ("dc_voltage", f),
                         ("pulse_voltage", f),
                         ("det_x", f),
                         ("det_y", f),
                         ("psl", i),
                         ("ipp", i)])

        data = n.fromfile(filepath, dtype=dtype)
        # data["dc_voltage"] *= 1000
        # data["pulse_voltage"] *= 1000

        retn = cls(data["xyz"],
                   data["mass"],
                   {"tof": data["tof"],
                    "dc_voltage": data["dc_voltage"],
                    "pulse_voltage": data["pulse_voltage"],
                    "det_x": data["det_x"],
                    "det_y": data["det_y"],
                    "psl": data["psl"],
                    "ipp": data["ipp"].astype(n.uint8)})
        retn._filepath = filepath
        retn._from_pos_or_epos = True
        return retn

    @classmethod
    def from_ato(cls, filepath: str):
        """
        Read the contents of an extended ato file into an Roi container. Suitable for multiple-hit analysis.

        :param filepath: Path to ato file
        """
        validate.file_exists(filepath)

        with open(filepath, "rb") as ato:
            ato.seek(8, os.SEEK_SET)
            f = "<f4"
            i = "<i4"
            dtype = n.dtype([("xyz", (f, 3)),
                             ("mass", f),
                             ("cluster_id", i),
                             ("pulse_number", f),
                             ("dc_voltage", f),  # kV
                             ("tof", f),
                             ("det_x", f),  # cm
                             ("det_y", f),  # cm
                             ("pulse_voltage", f),  # kV
                             ("vvolt", f),
                             ("fourier_r", f),
                             ("fourier_i", f)])

            data = n.fromfile(ato, dtype=dtype)

        # Process some data to make units consistent and other cleaning
        pulsen = data["pulse_number"].copy().astype(n.int64)
        diff = n.diff(data["pulse_number"])
        switch_idx = n.argwhere(diff < 0).ravel()
        begin = n.concatenate((n.array([0]), switch_idx + 1))
        end = n.concatenate((switch_idx, pulsen.shape))
        data["dc_voltage"] *= 1000  # to volts
        data["pulse_voltage"] *= 1000  # to volts
        data["tof"] *= 1e-3  # to nanoseconds

        for j, startstop in enumerate(zip(begin, end)):
            start, stop = startstop
            pulsen[start:stop+1] += j*2**24
        data["pulse_number"] = pulsen

        retn = cls(data["xyz"],
                   data["mass"],
                   {"tof": data["tof"],
                    "dc_voltage": data["dc_voltage"],
                    "pulse_voltage": data["pulse_voltage"],
                    "pulse_number": data["pulse_number"],
                    "det_x": data["det_x"],
                    "det_y": data["det_y"],
                    })
        retn._filepath = filepath
        return retn

    def memory_size(self) -> float:
        """
        Get the approximate memory footprint in Mb
        """
        val = getsizeof(self)
        val += self.xyz.nbytes
        val += self.mass.nbytes
        for i in self.misc.values():
            val += i.nbytes

        return round(val/1024**2, 3)

    def multiplicity_counts(self) -> Tuple[ndarray, ndarray]:
        """
        Get the statistical count of each degree of multiple-detector events
        """
        if not self.has_multiplicity_info():
            raise validate.NoMultiEventError()

        if self._multiplicity_counts is None:
            if self.multiplicities.size == 0:
                return n.array([]), n.array([])

            counts = n.zeros(self.multiplicities.size)
            for i, j in enumerate(self.multiplicities):
                counts[i] = get_mass_indices(self.misc["ipp"], j).size
                self._multiplicity_counts = self.multiplicities, counts

        return self._multiplicity_counts

    def multiplicity_percentage(self):
        """
        Get the statistical percentage of each degree of multiple-detector events
        """
        mult, counts = self.multiplicity_fraction()
        return mult, counts*100

    def multiplicity_fraction(self):
        """
        Get the statistical fraction of each degree of multiple-detector events
        """
        mult, counts = self.multiplicity_counts()
        return mult, counts/counts.sum()

    @lru_cache(50)
    def tof_histogram(self,
                      bin_width: float = 1,
                      multiplicity: Union[str, int] = "all",
                      norm: Union[bool, Tuple[float, float]] = False,
                      cutoff: float = 2000) -> (ndarray, ndarray):
        """
        Get the time-of-flight histogram of the given Roi. This function is cached to increase speed under repeated
        calls.

        :param bin_width: Bin width in Da
        :param multiplicity: The portion of multiplicity to generate the histogram from. "All" for all hits, int >= 1
            for a specific multiplicity, "multiples" for all multiple hits.
        :param norm: Normalize the histogram to unity. True/False to generate normalization constant from the whole
            spectrum, or Tuple[float, float] to generate normalization constant from a range on the spectrum.
        :param cutoff: Maximum time of flight value to generate the histogram
        """
        self.require_tof_info()
        validate.multiplicity_any(multiplicity)
        validate.positive_nonzero_number(bin_width)
        validate.positive_nonzero_number(cutoff)
        if multiplicity != "all":
            self.require_multihit_info()

        extents = (0, cutoff)

        # If multi-hit information is available
        if multiplicity == "all":
            counts, edges = histogram1d(self.misc["tof"], bin_width, extents)
        else:
            idxs = get_mass_indices(self.misc["ipp"], multiplicity)
            counts, edges = histogram1d(self.misc["tof"][idxs], bin_width, extents)

        # Normalization
        norm_val = 1
        if norm is True:
            norm_val = counts.max()
        elif isinstance(norm, (tuple, list)):
            # Range base normalization
            if len(norm) != 2 or (norm[1] <= norm[0]) or any(i < 0 for i in norm):
                raise ValueError("Invalid normalization range")

            norm_idx = n.argwhere((edges >= norm[0]) & (edges <= norm[1]))
            norm_val = counts[norm_idx].upper()

        counts /= norm_val

        return edges, counts

    @lru_cache(50)
    def mass_histogram(self,
                       bin_width: float = 0.05,
                       lower: float = 0,
                       upper: float = 200,
                       multiplicity: Union[str, int] = "all",
                       norm: Union[bool, Tuple[float, float]] = False) -> (ndarray, ndarray):
        """
        Get the mass/charge ratio histogram of the given Roi. This function is cached to increase speed under repeated
        calls.

        :param bin_width: Bin width in daltons
        :param lower: Minimum mass/charge ratio
        :param upper: Minimum mass/charge ratio
        :param multiplicity: The portion of multiplicity to generate the histogram from. "All" for all hits, int >= 1
            for a specific multiplicity, "multiples" for all multiple hits.
        :param norm: Normalize the histogram to unity. True/False to generate normalization constant from the whole
            spectrum, or Tuple[float, float] to generate normalization constant from a range on the spectrum.
        """
        validate.multiplicity_any(multiplicity)
        validate.positive_nonzero_number(bin_width)
        validate.positive_interval((lower, upper))

        if multiplicity != "all":
            self.require_multihit_info()

        extents = (lower, upper)

        # If multi-hit information is available
        if multiplicity == "all":
            counts, centers = histogram1d(self.mass, bin_width, extents)
        else:
            idxs = get_mass_indices(self.misc["ipp"], multiplicity)
            counts, centers = histogram1d(self.mass[idxs], bin_width, extents)

        # Normalization
        norm_val = 1
        if norm is True:
            norm_val = counts.max()
        elif isinstance(norm, (tuple, list)):
            # Range base normalization
            if len(norm) != 2 or (norm[1] <= norm[0]) or any(i < 0 for i in norm):
                raise ValueError("Invalid normalization range")

            norm_idx = n.argwhere((centers >= norm[0]) & (centers <= norm[1]))
            norm_val = counts[norm_idx].upper()

        counts /= norm_val

        return centers, counts

    def plot_mass_spectrum(self):
        """
        Get an interactive plot of the mass spectrum of the Roi.
        """
        return vfactory.make("mass_spectrum_plot", self)

    def require_multihit_info(self):
        """
        Use when a function/argument requires multiple hit information
        """
        if not self.has_multiplicity_info():
            raise NoMultiEventError()

    def require_detector_info(self):
        """
        Use when a function/argument requires detector information
        """
        if any(i not in self.misc.keys() for i in ("det_x", "det_y")):
            raise NoDetectorInfoError()

    def require_tof_info(self):
        """
        Use when a function/argument requires time of flight information
        """
        if "tof" not in self.misc:
            raise NoTOFError()


class RoiSubsetType(Roi):
    """
    For generating Roi instances from subsets of existing Roi. Also set certain restriction that otherwise
    would not make sense (such as file loading methods).
    """

    @classmethod
    def from_ato(cls, filepath: str):
        """
        Cannot load data into subset types
        """
        raise Exception("Loading files from roi subset types is not allowed")

    @classmethod
    def from_pos(cls, filepath: str):
        """
        Cannot load data into subset types
        """
        raise Exception("Loading files from roi subset types is not allowed")

    @classmethod
    def from_epos(cls, filepath: str):
        """
        Cannot load data into subset types
        """
        raise Exception("Loading files from roi subset types is not allowed")


class RoiRectPrism(RoiSubsetType):
    """
    Creates a new roi from an existing roi, containing ions within a rectangular prism
    """
    def __init__(self,
                 parent: Roi,
                 center: Tuple[float, float, float],
                 widths: Tuple[float, float, float]):
        """
        :param parent: Parent Roi to generate the subset from
        :param center: Geometric center to place the rectangular prism
        :param widths: x, y, z lengths of the rectangular prism
        """

        self._parent = parent
        self._center = center
        self._widths = validate.all_positive_nonzero(widths)

        super().__init__(parent.xyz, parent.mass, misc=parent.misc)
        self._from_pos_or_epos = self._parent._from_pos_or_epos

        xc, yc, zc = center
        dx, dy, dz = [width/2 for width in widths]

        # Axis boundaries
        xext, yext, zext = (xc-dx, xc+dx), \
                           (yc-dy, yc+dy), \
                           (zc-dz, zc+dz)
        xyz = self.xyz

        idx = n.argwhere((xext[0] < xyz[:, 0]) & (xyz[:, 0] < xext[1])).ravel()
        idx = idx[n.argwhere((yext[0] < xyz[idx][:, 1]) & (xyz[idx][:, 1] < yext[1])).ravel()]
        idx = idx[n.argwhere((zext[0] < xyz[idx][:, 2]) & (xyz[idx][:, 2] < zext[1])).ravel()]

        # First filter out everything outside of the bounding box
        # idx = n.argwhere((xext[0] < xyz[:, 0]) & (xyz[:, 0] < xext[1]) &
        #                  (yext[0] < xyz[:, 1]) & (xyz[:, 1] < yext[1]) &
        #                  (zext[0] < xyz[:, 2]) & (xyz[:, 2] < zext[1])).ravel()

        self._mask = idx


class RoiSphere(RoiSubsetType):
    """
    Creates a new roi from an existing roi, containing ions within a sphere
    """
    def __init__(self,
                 parent: Roi,
                 center: Tuple[float, float, float],
                 radius: float):
        """
        :param parent: Parent Roi to generate the subset from
        :param center: Geometric center of the sphere
        :param radius: Radius of the sphere
        """

        self._parent = parent
        self._center = center
        self._radius = validate.positive_nonzero_number(radius)

        super().__init__(parent.xyz, parent.mass, misc=parent.misc)
        self._from_pos_or_epos = self._parent._from_pos_or_epos

        xc, yc, zc = center

        # Axis boundaries
        xext, yext, zext = (xc-radius, xc+radius), \
                           (yc-radius, yc+radius), \
                           (zc-radius, zc+radius)
        xyz = self.xyz

        # First filter out everything outside of the bounding box
        idx = n.argwhere((xext[0] < xyz[:, 0]) & (xyz[:, 0] < xext[1])).ravel()
        idx = idx[n.argwhere((yext[0] < xyz[idx][:, 1]) & (xyz[idx][:, 1] < yext[1])).ravel()]
        idx = idx[n.argwhere((zext[0] < xyz[idx][:, 2]) & (xyz[idx][:, 2] < zext[1])).ravel()]

        # idx = n.argwhere((xext[0] < xyz[:, 0]) & (xyz[:, 0] < xext[1]) &
        #                  (yext[0] < xyz[:, 1]) & (xyz[:, 1] < yext[1]) &
        #                  (zext[0] < xyz[:, 2]) & (xyz[:, 2] < zext[1])).ravel()

        # Then filter out everything not within the sphere radius
        r = la.norm((xyz[idx]-center), axis=1)
        idx = idx[n.argwhere(r < radius).ravel()]

        self._mask = idx


class RoiCylinder(RoiSubsetType):
    """
    Creates a new roi from an existing roi, containing ions within a cylinder
    """
    def __init__(self,
                 parent: Roi,
                 center: Tuple[float, float, float],
                 radius: float,
                 height: float,
                 axis: str = "z"):
        """
        :param parent: Parent Roi to generate the subset from
        :param center: Geometric center to place the cylinder
        :param radius: Radius of the cylinder
        :param height: Height of the cylinder
        :param axis: Axis to orient the cylinder. Either "x", "y", or "z"
        """

        self._parent = parent
        self._center = center
        self._radius = validate.positive_nonzero_number(radius)
        self._height = validate.positive_nonzero_number(height)
        self._axis = validate.choice(axis, ("x", "y", "z"))

        super().__init__(parent.xyz, parent.mass, misc=parent.misc)
        self._from_pos_or_epos = self._parent._from_pos_or_epos

        xc, yc, zc = center
        axis_map = {"x": 0, "y": 1, "z": 2}

        # index of the axial direction
        axial_idx = axis_map[axis]

        # Indices of the non-axial directions
        non_axial_idx = [i for i in range(3) if i != axial_idx]

        # Map the axis to the value corresponding to the difference from the center to that axes' outer boundary
        diff_map = {ax: radius if ax != axis else height/2 for ax in ("x", "y", "z")}

        # Axis boundaries
        xext, yext, zext = (xc-diff_map["x"], xc+diff_map["x"]), \
                           (yc-diff_map["y"], yc+diff_map["y"]), \
                           (zc-diff_map["z"], zc+diff_map["z"])
        xyz = self.xyz

        # First filter out everything outside of the bounding box of the cylinder
        idx = n.argwhere((xext[0] < xyz[:, 0]) & (xyz[:, 0] < xext[1])).ravel()
        idx = idx[n.argwhere((yext[0] < xyz[idx][:, 1]) & (xyz[idx][:, 1] < yext[1])).ravel()]
        idx = idx[n.argwhere((zext[0] < xyz[idx][:, 2]) & (xyz[idx][:, 2] < zext[1])).ravel()]

        # idx = n.argwhere((xext[0] < xyz[:, 0]) & (xyz[:, 0] < xext[1]) &
        #                  (yext[0] < xyz[:, 1]) & (xyz[:, 1] < yext[1]) &
        #                  (zext[0] < xyz[:, 2]) & (xyz[:, 2] < zext[1])).ravel()

        # Then filter out everything not within the cylinder radius
        r = la.norm((xyz[idx]-center)[:, non_axial_idx], axis=1)
        idx = idx[n.argwhere(r < radius).ravel()]

        self._mask = idx


class DummyRoiHistogram(Roi):
    """
    This is a dummy roi class with an explicitly specified constant mass spectrum mass_histogram. This is used when an
    analysis needs to bypass loading the pos/epos data, such as when doing a MassSpectrum analysis on a mass spectrum
    from a csv file. One may choose to do this to avoid the cost of repeatedly loading very large datasets.
    """

    def __init__(self, x: ndarray, y: ndarray):
        """
        :param x: the x values of the mass histogram
        :param y: the y values of the mass histogram
        """
        super().__init__(n.array([[0, 0, 0]]), n.array([0]))
        self.__histogram = (x, y)

    def mass_histogram(self, *args, **kwargs):
        """
        Override :meth:`Roi.mass_histogram()` to always return the specified mass histogram
        """
        return self.__histogram
