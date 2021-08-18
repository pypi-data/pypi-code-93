import os
import pytest
import pkg_resources
from unittest import TestCase
import numpy as np
from astropy.time import Time
from dkist_processing_pac import Data
from dkist_processing_pac.utils import gen_fake_data

RTOL=1e-6
test_dir = pkg_resources.resource_filename('dkist_processing_pac', 'tests/data')
RUN1=test_dir+'/run1'
RUN2=test_dir+'/run2'
BADINST=test_dir+'/bad_inst'
BADDATE=test_dir+'/bad_date'
BADWAVE=test_dir+'/bad_wave'
BADMOD=test_dir+'/bad_mod'
BADSHAPE=test_dir+'/bad_shape'
DLDATA=test_dir+'/DL'
CRYODATA=test_dir+'/cryo'
LOWFLUX=test_dir+'/lowflux'
if (not os.path.exists(RUN1) and not os.path.isdir(RUN1))\
        or (not os.path.exists(RUN2) and not os.path.isdir(RUN2))\
        or (not os.path.exists(BADINST) and not os.path.isdir(BADINST))\
        or (not os.path.exists(BADDATE) and not os.path.isdir(BADDATE))\
        or (not os.path.exists(BADWAVE) and not os.path.isdir(BADWAVE))\
        or (not os.path.exists(BADMOD) and not os.path.isdir(BADMOD))\
        or (not os.path.exists(BADSHAPE) and not os.path.isdir(BADSHAPE))\
        or (not os.path.exists(DLDATA) and not os.path.isdir(DLDATA))\
        or (not os.path.exists(LOWFLUX) and not os.path.isdir(LOWFLUX))\
        or (not os.path.exists(CRYODATA) and not os.path.isdir(CRYODATA)):
    gen_fake_data.make_testing_data()

def get_telescope_geometry(PCD):

    times = PCD.timeobs

    ele = np.zeros(PCD.numsteps)
    az = np.zeros(PCD.numsteps)
    tab = np.zeros(PCD.numsteps)
    for n in range(PCD.numsteps):
        obstime = Time(times[n], format='mjd')
        tele, taz, ttab = gen_fake_data.compute_telgeom(obstime)
        ele[n] = tele
        az[n] = taz
        tab[n] = ttab

    return az, ele, tab

class TestMuellerMatrices(TestCase):

    def test_linear_retarder(self):
        np.testing.assert_allclose(Data.linear_retarder(1,0,0), np.diag(np.ones(4)), rtol=RTOL)

    def test_rotation(self):
        np.testing.assert_allclose(Data.rotation(0), np.diag(np.ones(4)), rtol=RTOL)

    def test_mirror(self):
        np.testing.assert_allclose(Data.mirror(1,0), np.diag(np.ones(4)), rtol=RTOL)

class TestInit(TestCase):

    def test_bare_init(self):
        PCD = Data.Drawer()

        self.assertEqual(PCD.data_list, [])
        self.assertEqual(PCD.instrument, '')
        self.assertEqual(PCD.theta_ret_steps.size, 0)

    def test_with_instrument(self):
        PCD = Data.Drawer(instrument='visp')

        self.assertEqual(PCD.modid_key, 'VISP_011')
        self.assertEqual(PCD.modnum_key, 'VISP_010')

    def test_with_directory(self):
        PCD = Data.Drawer(data_dir=RUN1)

        self.assertEqual(PCD.instrument.lower(), 'visp')
        self.assertEqual(PCD.theta_ret_steps.size, 5)

class TestLoadFromDir(TestCase):

    def test_basic_load(self):
        PCD = Data.Drawer()
        PCD.load_from_dir(RUN1)

        true_az, true_ele, true_tab = get_telescope_geometry(PCD)

        self.assertEqual(PCD.instrument.lower(), 'visp')
        self.assertEqual(PCD.nummod, 10)
        self.assertEqual(PCD.numsteps, 5)
        self.assertEqual(PCD.wavelength, 620.)
        self.assertEqual(PCD.date_bgn, 57530)
        self.assertAlmostEqual(PCD.date_end, 57530.00104166667)
        self.assertEqual(len(PCD.data_list), 5)
        self.assertEqual(len(PCD.data_list[0]), 11)
        np.testing.assert_array_equal(PCD.theta_pol_steps, np.linspace(0, 360, 5))
        np.testing.assert_array_equal(PCD.theta_ret_steps, np.array([27.5, 22.5, 27.5, 22.5, 27.5]))
        np.testing.assert_array_equal(PCD.pol_in, np.array([True, True, True, True, True]))
        np.testing.assert_array_equal(PCD.ret_in, np.array([True, False, True, True, False]))
        np.testing.assert_array_almost_equal(PCD.timeobs, np.arange(5) * 15 / (3600 * 24) + 57530 + 15 / (3600 * 24))
        np.testing.assert_allclose(PCD.azimuth, true_az)
        np.testing.assert_allclose(PCD.elevation, true_ele)
        np.testing.assert_allclose(PCD.table_angle, true_tab)

    def test_no_skip_darks(self):
        PCD = Data.Drawer()
        PCD.load_from_dir(RUN1, skip_darks=False)

        true_az, true_ele, true_tab = get_telescope_geometry(PCD)

        self.assertEqual(PCD.instrument.lower(), 'visp')
        self.assertEqual(PCD.nummod, 10)
        self.assertEqual(PCD.numsteps, 7)
        self.assertEqual(PCD.wavelength, 620.)
        self.assertEqual(PCD.date_bgn, 57530)
        self.assertAlmostEqual(PCD.date_end, 57530.00104166667)
        self.assertEqual(len(PCD.data_list), 7)
        self.assertEqual(len(PCD.data_list[0]), 11)
        np.testing.assert_array_equal(PCD.theta_pol_steps, np.r_[np.array([0]), np.linspace(0, 360, 5), np.array([0])])
        np.testing.assert_array_equal(PCD.theta_ret_steps, np.array([22.5, 27.5, 22.5, 27.5, 22.5, 27.5, 22.5]))
        np.testing.assert_array_equal(PCD.pol_in, np.array([True, True, True, True, True, True, True]))
        np.testing.assert_array_equal(PCD.ret_in, np.array([True, True, False, True, True, False, True]))
        np.testing.assert_array_almost_equal(PCD.timeobs, np.arange(7) * 15 / (3600 * 24) + 57530)
        np.testing.assert_allclose(PCD.azimuth, true_az)
        np.testing.assert_allclose(PCD.elevation, true_ele)
        np.testing.assert_allclose(PCD.table_angle, true_tab)

    def test_bad_instrument(self):
        PCD = Data.Drawer()
        with self.assertRaisesRegex(ValueError, 'Not all input files were taken with the same instrument'):
            PCD.load_from_dir(BADINST)

    @pytest.mark.skip
    def test_bad_date(self):
        PCD = Data.Drawer()
        with self.assertRaisesRegex(ValueError, 'Not all input files have the same start/end dates'):
            PCD.load_from_dir(BADDATE)

    def test_bad_wavelength(self):
        PCD = Data.Drawer()
        with self.assertRaisesRegex(ValueError, 'Not all input files were taken at the same wavelength'):
            PCD.load_from_dir(BADWAVE)

    def test_bad_modnum(self):
        PCD = Data.Drawer()
        with self.assertRaisesRegex(ValueError, 'Not all input files have the same number of modulator states'):
            PCD.load_from_dir(BADMOD)

class TestIntensityFit(TestCase):

    def test_low_clear_flux(self):

        PCD = Data.Drawer(LOWFLUX, remove_I_trend=False)
        with self.assertRaisesRegex(ValueError, 'Flux in Clear measurements is too low'):
            PCD.find_clears()
            PCD.fit_intensity_trend()

class TestAddition(TestCase):

    def test_concatenation(self):
        PCD1 = Data.Drawer(RUN1)
        PCD2 = Data.Drawer(RUN2)
        PCD = PCD1 + PCD2

        az1, ele1, tab1 = get_telescope_geometry(PCD1)
        az2, ele2, tab2 = get_telescope_geometry(PCD2)

        true_az = np.r_[az1, az2]
        true_ele = np.r_[ele1, ele2]
        true_tab = np.r_[tab1, tab2]

        self.assertEqual(PCD.instrument.lower(), 'visp')
        self.assertEqual(PCD.nummod, 10)
        self.assertEqual(PCD.numsteps, 10)
        self.assertEqual(PCD.wavelength, 620.)
        self.assertEqual(PCD.date_bgn, 57530)
        self.assertEqual(PCD.RN, 13.)
        self.assertAlmostEqual(PCD.date_end, 57560.00104166667)
        self.assertEqual(len(PCD.data_list), 10)
        self.assertEqual(len(PCD.data_list[0]), 11)
        np.testing.assert_array_equal(PCD.theta_pol_steps, np.r_[np.linspace(0, 360, 5), np.ones(5)*180])
        np.testing.assert_array_equal(PCD.theta_ret_steps, np.r_[np.array([27.5, 22.5, 27.5, 22.5, 27.5]), np.linspace(0,360,5)])
        np.testing.assert_array_equal(PCD.pol_in, np.array([True, True, True, True, True, True, True, True, True, True]))
        np.testing.assert_array_equal(PCD.ret_in, np.array([True, False, True, True, False, True, False, True, True, False]))
        np.testing.assert_array_almost_equal(PCD.timeobs, 15 / (24 * 3600) + np.r_[np.arange(5) * 15 / (3600 * 24) + 57530, np.arange(5) * 15/(3600*24) + 57560.])
        np.testing.assert_allclose(PCD.azimuth, true_az)
        np.testing.assert_allclose(PCD.elevation, true_ele)
        np.testing.assert_allclose(PCD.table_angle, true_tab)

    def test_new_object(self):
        PCD1 = Data.Drawer(RUN1)
        PCD2 = Data.Drawer(RUN2)
        PCD = PCD1 + PCD2

        self.assertIsNot(PCD1, PCD)

class TestSlice(TestCase):

    def setUp(self):
        self.PCD = Data.Drawer(RUN1)

    def tearDown(self):
        del self.PCD

    def test_basic_slice(self):
        I = self.PCD[2,1,0]
        self.assertEqual(I.shape, (10,5))
        self.assertIs(type(I), np.ndarray)
        self.assertEqual(I.dtype, np.float64)

    def test_bad_slice(self):
        with self.assertRaisesRegex(IndexError, 'Drawer must be indexed by exactly three values'):
            I = self.PCD[1,0]

    def test_bad_slice2(self):
        with self.assertRaisesRegex(IndexError, 'Drawer must be indexed by exactly three values'):
            I = self.PCD[0]

    def test_non_int(self):
        with self.assertRaisesRegex(IndexError, 'Only integers are allowed as valid indices'):
            I = self.PCD[0,1.1,0]

    def test_colon(self):
        with self.assertRaisesRegex(IndexError, 'Only integers are allowed as valid indices'):
            I = self.PCD[0,:,0]

class TestShapes(TestCase):

    def test_shape(self):
        PCD = Data.Drawer(RUN1)
        self.assertEqual(PCD.shape, (3,2,1))

    def test_wrong_shape(self):
        with self.assertRaisesRegexp(ValueError,'Data do not appear to have 3 dimensions.*'):
            PCD = Data.Drawer(BADSHAPE)

class TestUncertainty(TestCase):
    def setUp(self):
        self.PCD = Data.Drawer(RUN2)

    def tearDown(self):
        del self.PCD

    def test_correct_RN(self):
        self.assertEqual(self.PCD.RN, 13.)

    def test_correct_unc(self):
        I = self.PCD[0,0,0]
        u = self.PCD.get_uncertainty(I)
        np.testing.assert_array_equal(u, np.sqrt(np.abs(I) + self.PCD.RN**2))

    def test_correct_dresser(self):
        PCD1 = Data.Drawer(RUN1)
        I1 = PCD1[0,0,0]
        I2 = self.PCD[0,0,0]
        DRSR = Data.Dresser()
        DRSR.add_drawer(PCD1)
        DRSR.add_drawer(self.PCD)
        I, u = DRSR[0,0,0]
        np.testing.assert_array_equal(u, np.hstack((PCD1.get_uncertainty(I1), self.PCD.get_uncertainty(I2))))

class TestDresser(TestCase):

    def setUp(self):
        self.DRSR = Data.Dresser()
        self.PCD1 = Data.Drawer(RUN1)
        self.DRSR.add_drawer(self.PCD1)
        self.PCD2 = Data.Drawer(RUN2)
        self.DRSR.add_drawer(self.PCD2)

    def tearDown(self):
        del self.DRSR
        del self.PCD1
        del self.PCD2

    def test_numdrawer(self):
        self.assertEqual(self.DRSR.numdrawers, 2)

    def test_numsteps(self):
        self.assertEqual(self.DRSR.numsteps, 10)

    def test_numsteps_nodarkskip(self):
        DRSR = Data.Dresser()
        DRSR.add_drawer(Data.Drawer(RUN1, skip_darks=False))
        DRSR.add_drawer(Data.Drawer(RUN2, skip_darks=False))
        self.assertEqual(DRSR.numsteps, 14)

    def test_step_list(self):
        self.assertEqual(self.DRSR.drawer_step_list, [5,5])

    def test_step_list_nodarkskip(self):
        DRSR = Data.Dresser()
        DRSR.add_drawer(Data.Drawer(RUN1, skip_darks=False))
        DRSR.add_drawer(Data.Drawer(RUN2, skip_darks=False))
        self.assertEqual(DRSR.drawer_step_list, [7,7])

    def test_shape(self):
        self.assertEqual(self.DRSR.shape, (3,2,1))

    def test_wrong_modnum(self):
        DRSR = Data.Dresser()
        DRSR.nummod = 99
        with self.assertRaisesRegex(ValueError, 'Trying to add Drawer with 10 mod states to Dresser with 99'):
            DRSR.add_drawer(Data.Drawer(RUN1))

    def test_wrong_wave(self):
        DRSR = Data.Dresser()
        DRSR.wavelength = 999
        with self.assertRaisesRegex(ValueError, 'Drawer with wave = .*620\.0 cannot be added to Dresser with wave = .*999\.0'):
            DRSR.add_drawer(Data.Drawer(RUN1))

    def test_wrong_instrument(self):
        DRSR = Data.Dresser()
        DRSR.instrument = 'NOTHING'
        with self.assertRaisesRegex(ValueError, 'Drawer from instrument VISP cannot be added to Dresser from instrument NOTHING'):
            DRSR.add_drawer(Data.Drawer(RUN1))

    def test_wrong_shape(self):
        DRSR = Data.Dresser()
        DRSR.shape = (99,)
        with self.assertRaisesRegex(ValueError, 'Drawer with shape \(3, 2, 1\) does not fit into Dresser with shape \(99,\)'):
            DRSR.add_drawer(Data.Drawer(RUN1))

    def test_get_item_correct(self):
        truth = np.hstack((self.PCD1[0,0,0], self.PCD2[0,0,0]))
        np.testing.assert_array_equal(self.DRSR[0,0,0][0], truth)

class TestVISPKeywords(TestCase):
    def setUp(self):
        self.PCD = Data.Drawer(RUN1)

    def tearDown(self):
        del self.PCD

    def test_modid(self):
        self.assertEqual(self.PCD.data_list[0][1].header[self.PCD.modid_key], 1)
        self.assertEqual(self.PCD.data_list[0][2].header[self.PCD.modid_key], 2)
        self.assertEqual(self.PCD.data_list[0][3].header[self.PCD.modid_key], 3)
        self.assertEqual(self.PCD.data_list[0][4].header[self.PCD.modid_key], 4)
        self.assertEqual(self.PCD.data_list[0][5].header[self.PCD.modid_key], 5)
        self.assertEqual(self.PCD.data_list[0][6].header[self.PCD.modid_key], 6)
        self.assertEqual(self.PCD.data_list[0][7].header[self.PCD.modid_key], 7)
        self.assertEqual(self.PCD.data_list[0][8].header[self.PCD.modid_key], 8)
        self.assertEqual(self.PCD.data_list[0][9].header[self.PCD.modid_key], 9)
        self.assertEqual(self.PCD.data_list[0][10].header[self.PCD.modid_key], 10)

    def test_modnum(self):
        self.assertEqual(self.PCD.data_list[0][0].header[self.PCD.modnum_key], 10)
        self.assertEqual(self.PCD.data_list[0][5].header[self.PCD.modnum_key], 10)


class TestDLNIRSPKeywords(TestCase):
    def setUp(self):
        self.PCD = Data.Drawer(DLDATA)

    def tearDown(self):
        del self.PCD

    def test_modid(self):
        self.assertEqual(self.PCD.data_list[0][1].header[self.PCD.modid_key], 0)
        self.assertEqual(self.PCD.data_list[0][2].header[self.PCD.modid_key], 1)
        self.assertEqual(self.PCD.data_list[0][3].header[self.PCD.modid_key], 2)
        self.assertEqual(self.PCD.data_list[0][4].header[self.PCD.modid_key], 3)
        self.assertEqual(self.PCD.data_list[0][5].header[self.PCD.modid_key], 4)
        self.assertEqual(self.PCD.data_list[0][6].header[self.PCD.modid_key], 5)
        self.assertEqual(self.PCD.data_list[0][7].header[self.PCD.modid_key], 6)
        self.assertEqual(self.PCD.data_list[0][8].header[self.PCD.modid_key], 7)
        self.assertEqual(self.PCD.data_list[0][9].header[self.PCD.modid_key], 8)
        self.assertEqual(self.PCD.data_list[0][10].header[self.PCD.modid_key], 9)

    def test_modnum(self):
        self.assertEqual(self.PCD.data_list[0][0].header[self.PCD.modnum_key], 10)
        self.assertEqual(self.PCD.data_list[0][5].header[self.PCD.modnum_key], 10)

class TestCRYONIRSPKeywords(TestCase):
    def setUp(self):
        self.PCD = Data.Drawer(CRYODATA)

    def tearDown(self):
        del self.PCD

    def test_modid(self):
        self.assertEqual(self.PCD.data_list[0][1].header[self.PCD.modid_key], 0)
        self.assertEqual(self.PCD.data_list[0][2].header[self.PCD.modid_key], 1)
        self.assertEqual(self.PCD.data_list[0][3].header[self.PCD.modid_key], 2)
        self.assertEqual(self.PCD.data_list[0][4].header[self.PCD.modid_key], 3)
        self.assertEqual(self.PCD.data_list[0][5].header[self.PCD.modid_key], 4)
        self.assertEqual(self.PCD.data_list[0][6].header[self.PCD.modid_key], 5)
        self.assertEqual(self.PCD.data_list[0][7].header[self.PCD.modid_key], 6)
        self.assertEqual(self.PCD.data_list[0][8].header[self.PCD.modid_key], 7)
        self.assertEqual(self.PCD.data_list[0][9].header[self.PCD.modid_key], 8)
        self.assertEqual(self.PCD.data_list[0][10].header[self.PCD.modid_key], 9)

    def test_modnum(self):
        self.assertEqual(self.PCD.data_list[0][0].header[self.PCD.modnum_key], 10)
        self.assertEqual(self.PCD.data_list[0][5].header[self.PCD.modnum_key], 10)
