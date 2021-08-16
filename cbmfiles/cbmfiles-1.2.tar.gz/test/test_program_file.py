import unittest
from unittest.mock import patch, Mock
import io

from cbm_files.program_file import ProgramFile


class TestProgramFile(unittest.TestCase):
    def test_program_file(self):
        mock_file = io.BytesIO(b'\x01\x12\x00\x00\x00')
        with patch('cbm_files.program_file.BASICFile', new=Mock):
            f = ProgramFile(mock_file)
        self.assertTrue(isinstance(f, Mock))

    def test_binary_file(self):
        mock_file = io.BytesIO(b'\x00\x20\x00\x00\x00')
        with patch('cbm_files.program_file.BinaryFile', new=Mock):
            f = ProgramFile(mock_file)
        self.assertTrue(isinstance(f, Mock))
