import unittest

from pathlib import Path
from unittest.mock import patch, mock_open, Mock

from cbm_files.pc64_file import PC64File


class TestMagic(unittest.TestCase):

    def test_good_magic(self):
        with patch.object(Path, 'open', mock_open(read_data=b'C64File\x00')):
            self.assertTrue(PC64File.is_valid_image(Path()))

    def test_bad_magic(self):
        with patch.object(Path, 'open', mock_open(read_data=b'INVALID')):
            self.assertFalse(PC64File.is_valid_image(Path()))


class TestPrg(unittest.TestCase):

    def test_prg(self):
        mock_file = Mock()
        mock_file.name = 'test.p00'
        mock_file.read.side_effect = [b'C64File\x00',
                                      b'TEST\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']
        pc64 = PC64File(mock_file)
        self.assertEqual(pc64.name, b'TEST')
        self.assertEqual(pc64.file_type, 'PRG')


class TestRel(unittest.TestCase):

    def test_prg(self):
        mock_file = Mock()
        mock_file.name = 'test.r00'
        mock_file.read.side_effect = [b'C64File\x00',
                                      b'TEST\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x50']
        pc64 = PC64File(mock_file)
        self.assertEqual(pc64.name, b'TEST')
        self.assertEqual(pc64.file_type, 'REL')
        self.assertEqual(pc64.record_len, 80)


class TestSeq(unittest.TestCase):

    def test_prg(self):
        mock_file = Mock()
        mock_file.name = 'test.s01'
        mock_file.read.side_effect = [b'C64File\x00',
                                      b'TEST\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']
        pc64 = PC64File(mock_file)
        self.assertEqual(pc64.name, b'TEST')
        self.assertEqual(pc64.file_type, 'SEQ')
