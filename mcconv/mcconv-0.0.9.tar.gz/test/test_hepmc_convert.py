from mcconv import GenericTextReader, UnparsedTextEvent, hepmc_convert

import os
import unittest
from mcconv import detect_mc_type, McFileTypes
from pyHepMC3 import HepMC3 as hm

class TestGenericTextReader(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def _data_path(self, file_name):
        """Gets data file path"""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, 'data', file_name)

    def _tmp_path(self, file_name):
        """Gets output temporary file path"""

        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tmp', file_name)

    def test_convert_lund_gemc(self):
        """Test detecting BeaGLE file type"""

        hepmc_convert(self._data_path('gemc-lund.3evt.txt'),
                      self._tmp_path('lund-convert.hepmc'),
                      McFileTypes.LUND_GEMC, "hepmc3")

        # inputA = hm.ReaderAscii(self._tmp_path('lund-convert.hepmc'))
        # if inputA.failed():
        #     raise "inputA.failed()"
        #
        # while not inputA.failed():
        #     evt = hm.GenEvent()
        #     inputA.read_event(evt)
        #
        #     print(len(evt.particles()))
        #     evt.clear()
        # inputA.close()


    def test_convert_py6_eic(self):
        """Test detecting BeaGLE file type"""
        hepmc_convert(self._data_path('pythia6-radcor-10evt.txt'),
                      self._tmp_path('pythia6-radcor-10evt.hepmc'),
                      McFileTypes.UNKNOWN, "hepmc2")

        # print(dir(hm))
        # inputA = hm.ReaderAsciiHepMC2(self._tmp_path('pythia6-radcor-10evt.hepmc'))
        # if inputA.failed():
        #     raise "inputA.failed()"
        #
        # while not inputA.failed():
        #     evt = hm.GenEvent()
        #     inputA.read_event(evt)
        #
        #     print(len(evt.particles()))
        #     evt.clear()
        # inputA.close()
