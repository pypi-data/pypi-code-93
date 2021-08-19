from mcconv import detect_mc_type

import os
import unittest
from mcconv import detect_mc_type, McFileTypes


class TestStringMethods(unittest.TestCase):

    def setUp(self) -> None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(dir_path, 'data')

    def _get_file_path(self, path):
        """Gets data file path"""
        return os.path.join(self.data_path, path)


    def test_beagle(self):
        """Test detecting BeaGLE file type"""

        result = detect_mc_type(self._get_file_path('beagle_3events.txt'))
        self.assertEqual(result, McFileTypes.BEAGLE)

    def test_hepmc2(self):
        """Test detecting HepMC2 file type"""

        result = detect_mc_type(self._get_file_path('hepmc2.hepmc'))
        self.assertEqual(result, McFileTypes.HEPMC2)

    def test_hepmc3(self):
        """Test detecting BeaGLE file type"""

        result = detect_mc_type(self._get_file_path('hepmc3.hepmc'))
        self.assertEqual(result, McFileTypes.HEPMC3)

    def test_lund(self):
        result = detect_mc_type(self._get_file_path('gemc-lund.3evt.txt'))
        self.assertEqual(result, McFileTypes.LUND_GEMC)

    def test_pythia6radcor(self):
        result = detect_mc_type(self._get_file_path('pythia6-radcor-10evt.txt'))
        self.assertEqual(result, McFileTypes.PYTHIA6_EIC)

    def test_eic_smear(self):
        result = detect_mc_type(self._get_file_path('eic_DEMPGen_10on100_1B_1_100.root'))
        self.assertEqual(result, McFileTypes.EIC_SMEAR)

if __name__ == '__main__':
    unittest.main()