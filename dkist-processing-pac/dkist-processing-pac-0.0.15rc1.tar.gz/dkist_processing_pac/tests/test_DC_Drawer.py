import os
from collections import defaultdict
from glob import glob
from typing import Dict, Union
from typing import List
from typing import Tuple

import numpy as np
from astropy.io import fits as pyfits
import pytest
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator import spec122_validator

from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess

from dkist_processing_pac import Data, FittingFramework, generic, GenerateDemodMatrices
from dkist_processing_pac.DKISTDC.data import DCDrawer
from dkist_processing_pac.utils import gen_fake_data


class CalibrationSequenceDataset(Spec122Dataset):
    def __init__(
        self,
        array_shape: Tuple[int, ...],
        time_delta: float,
        instrument="visp",
    ):
        self.num_mod = 3

        # Make up a Calibration sequence. Mostly random except for two clears and two darks at start and end, which
        # we want to test
        self.pol_status = [
            "clear",
            "clear",
            "Polarizer",
            "Polarizer",
            "Polarizer",
            "clear",
            "clear",
        ]
        self.pol_theta = [0.0, 0.0, 60.0, 60.0, 120.0, 0.0, 0.0]
        self.ret_status = ["clear", "clear", "clear", "SAR", "clear", "clear", "clear"]
        self.ret_theta = [0.0, 0.0, 0.0, 45.0, 0.0, 0.0, 0.0]
        self.dark_status = [
            "DarkShutter",
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
            "DarkShutter",
        ]

        self.num_steps = len(self.pol_theta)
        dataset_shape = (self.num_steps * self.num_mod,) + array_shape[1:]
        super().__init__(dataset_shape, array_shape, time_delta, instrument=instrument)
        self.add_constant_key("DKIST004", "polcal")
        self.add_constant_key("WAVELNTH", 666.)

    @property
    def cs_step(self) -> int:
        return self.index // self.num_mod

    @key_function("VISP_011")
    def modstate(self, key: str) -> int:
        return (self.index % self.num_mod) + 1

    @key_function("VISP_010")
    def nummod(self, key: str) -> int:
        return self.num_mod

    @key_function("PAC__004")
    def polarizer_status(self, key: str) -> str:
        return self.pol_status[self.cs_step]

    @key_function("PAC__005")
    def polarizer_angle(self, key: str) -> str:
        return str(self.pol_theta[self.cs_step])

    @key_function("PAC__006")
    def retarter_status(self, key: str) -> str:
        return self.ret_status[self.cs_step]

    @key_function("PAC__007")
    def retarder_angle(self, key: str) -> str:
        return str(self.ret_theta[self.cs_step])

    @key_function("PAC__008")
    def gos_level3_status(self, key: str) -> str:
        return self.dark_status[self.cs_step]

class InstAccess(L0FitsAccess):
    def __init__(self, hdu: Union[pyfits.ImageHDU, pyfits.PrimaryHDU, pyfits.CompImageHDU]):
        super().__init__(hdu, auto_squeeze=False)
        self.mod_state = self.header["VISP_011"]
        self.num_mod_states = self.header["VISP_010"]

@pytest.fixture(scope="session")
def cs_step_obj_dict() -> Dict[int, List[InstAccess]]:
    ds = CalibrationSequenceDataset(array_shape=(1, 2, 2), time_delta=2.0)
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=pyfits.HDUList)[0].header
        for d in ds
    ]
    out_dict = dict()
    for n in range(7):
        hdu_list = []
        for m in range(3):
            hdu_list.append(pyfits.PrimaryHDU(data=np.ones((3, 4, 1)) * n + 100 * m, header=pyfits.Header(header_list.pop(0))))

        out_dict[n] = [InstAccess(h) for h in hdu_list]

    return out_dict

@pytest.fixture(scope="session")
def SoCC_dir(tmpdir_factory):
    SoCC_dir = tmpdir_factory.mktemp("SoCC")
    num_pos = 5
    gen_fake_data.SoCC_multi_day(SoCC_dir, numdays=1, shape=(1, 1, num_pos), DHS=False, CS_name='may_CS')

    return str(SoCC_dir / 'day0')

@pytest.fixture(scope="function")
def DC_SoCC(SoCC_dir):
    file_list = sorted(glob(os.path.join(SoCC_dir, '*.FITS')))
    obj_dict = defaultdict(list)
    for i, f in enumerate(file_list):
        hdl = pyfits.open(f)
        for h in hdl[1:]:
            t_head = spec122_validator.validate_and_translate_to_214_l0(h.header, return_type=pyfits.HDUList)[0].header
            obj_dict[i].append(InstAccess(pyfits.ImageHDU(data=h.data, header=t_head)))

    return obj_dict


def test_dkistdc_drawer(cs_step_obj_dict):

    D = DCDrawer(cs_step_obj_dict, remove_I_trend=False)
    assert D.nummod == 3
    assert D.numsteps == 7 - 2
    np.testing.assert_array_equal(D.pol_in, [False, True, True, True, False])
    np.testing.assert_array_equal(D.theta_pol_steps, [0.0, 60.0, 60.0, 120.0, 0.0])
    np.testing.assert_array_equal(D.ret_in, [False, False, True, False, False])
    np.testing.assert_array_equal(D.theta_ret_steps, [0.0, 0.0, 45.0, 0.0, 0.0])
    np.testing.assert_array_equal(D.dark_in, [False, False, False, False, False])
    assert D.shape == (3, 4, 1)
    cc = np.ones((3, 5)) * np.arange(1, 6)[None, :] + 100 * np.arange(3)[:, None]
    for i in range(np.prod(D.shape)):
        np.testing.assert_array_equal(D[np.unravel_index(i, D.shape)], cc)

def test_dkistdc_drawer_with_darks(cs_step_obj_dict):

    D = DCDrawer(cs_step_obj_dict, skip_darks=False, remove_I_trend=False)
    assert D.nummod == 3
    assert D.numsteps == 7
    np.testing.assert_array_equal(D.pol_in, [False, False, True, True, True, False, False])
    np.testing.assert_array_equal(D.theta_pol_steps, [0.0, 0.0, 60.0, 60.0, 120.0, 0.0, 0.0])
    np.testing.assert_array_equal(D.ret_in, [False, False, False, True, False, False, False])
    np.testing.assert_array_equal(D.theta_ret_steps, [0.0, 0.0, 0.0, 45.0, 0.0, 0.0, 0.0])
    np.testing.assert_array_equal(D.dark_in, [True, False, False, False, False, False, True])
    assert D.shape == (3, 4, 1)
    cc = np.ones((3, 7)) * np.arange(7)[None, :] + 100 * np.arange(3)[:, None]
    for i in range(np.prod(D.shape)):
        np.testing.assert_array_equal(D[np.unravel_index(i, D.shape)], cc)

def test_dkistdc_drawer_I_trend(cs_step_obj_dict):

    D = DCDrawer(cs_step_obj_dict, remove_I_trend=True)
    assert D.shape == (3, 4, 1)
    cc = np.ones((3, 5)) * np.arange(1, 6)[None, :] + 100 * np.arange(3)[:, None]
    cc /= np.arange(1, 6) * 0.00970874 + 0.97087379
    for i in range(np.prod(D.shape)):
        np.testing.assert_allclose(D[np.unravel_index(i, D.shape)], cc)

def test_dresser(cs_step_obj_dict):

    D1 = DCDrawer(cs_step_obj_dict, skip_darks=False, remove_I_trend=False)
    D2 = DCDrawer(cs_step_obj_dict, skip_darks=True, remove_I_trend=False)
    DRSR = Data.Dresser()
    DRSR.add_drawer(D1)
    DRSR.add_drawer(D2)

    assert DRSR.nummod == 3
    assert DRSR.numsteps == 7 + 7 - 2
    np.testing.assert_array_equal(DRSR.pol_in,
                                  [False, False, True, True, True, False, False] + [False, True, True, True, False])
    np.testing.assert_array_equal(DRSR.theta_pol_steps,
                                  [0.0, 0.0, 60.0, 60.0, 120.0, 0.0, 0.0] + [0.0, 60.0, 60.0, 120.0, 0.0])
    np.testing.assert_array_equal(DRSR.ret_in,
                                  [False, False, False, True, False, False, False] + [False, False, True, False, False])
    np.testing.assert_array_equal(DRSR.theta_ret_steps,
                                  [0.0, 0.0, 0.0, 45.0, 0.0, 0.0, 0.0] + [0.0, 0.0, 45.0, 0.0, 0.0])
    np.testing.assert_array_equal(DRSR.dark_in,
                                  [True, False, False, False, False, False, True] + [False, False, False, False, False])
    assert DRSR.shape == (3, 4, 1)
    cc1 = np.ones((3, 7)) * np.arange(7)[None, :] + 100 * np.arange(3)[:, None]
    cc2 = np.ones((3, 5)) * np.arange(1, 6)[None, :] + 100 * np.arange(3)[:, None]
    cc = np.hstack([cc1, cc2])
    for i in range(np.prod(DRSR.shape)):
        np.testing.assert_array_equal(DRSR[np.unravel_index(i, DRSR.shape)][0], cc)

def test_same_dresser_as_non_DC(SoCC_dir, DC_SoCC):
    DRSR = Data.Dresser()
    DRSR.add_drawer(Data.Drawer(SoCC_dir))

    dc_DRSR = Data.Dresser()
    dc_DRSR.add_drawer(DCDrawer(DC_SoCC))

    for attr in ['instrument', 'nummod', 'numsteps', 'shape', 'theta_pol_steps', 'theta_ret_steps', 'pol_in',
                 'ret_in', 'date_bgn', 'date_end', 'wavelength', 'azimuth', 'elevation', 'table_angle',
                 'I_clear']:
        print(attr)
        if type(getattr(DRSR, attr)) is np.ndarray:
            np.testing.assert_equal(getattr(DRSR, attr), getattr(dc_DRSR, attr))
        else:
            assert getattr(DRSR, attr) == getattr(dc_DRSR, attr)

    for i in range(np.prod(DRSR.shape)):
        idx = np.unravel_index(i, DRSR.shape)
        np.testing.assert_array_equal(DRSR[idx][0], dc_DRSR[idx][0])
        np.testing.assert_array_equal(DRSR[idx][1], dc_DRSR[idx][1])

@pytest.mark.slow
def test_same_fit_and_demod_as_non_DC(SoCC_dir, DC_SoCC, tmp_path):
    CMP, TMP, TM = FittingFramework.run_fits([SoCC_dir], fit_TM=False, threads=2,
                                             telescope_db=generic.get_default_telescope_db())
    cmp_file = tmp_path / 'cmp.fits'
    CMP.writeto(cmp_file)

    DRSR = Data.Dresser()
    DRSR.add_drawer(DCDrawer(DC_SoCC))
    dc_CMP, dc_TMP, dc_TM = FittingFramework.run_core(DRSR, fit_TM=False, threads=2,
                                             telescope_db=generic.get_default_telescope_db())

    np.testing.assert_equal(CMP.CU_params, dc_CMP.CU_params)
    np.testing.assert_equal(TMP.TM_params, dc_TMP.TM_params)

    dmod_file = tmp_path / 'dmod.fits'
    GenerateDemodMatrices.main(SoCC_dir, str(cmp_file), str(dmod_file),
                               telescope_db=generic.get_default_telescope_db())
    dhdl = pyfits.open(dmod_file)
    dmod = dhdl[1].data

    dc_dmod = GenerateDemodMatrices.DC_main(DRSR, dc_CMP, telescope_db=generic.get_default_telescope_db())
    np.testing.assert_equal(dmod, dc_dmod)
