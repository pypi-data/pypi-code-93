import tempfile
import unittest
from unittest.mock import patch

import pytest

from feyn._config import _resolve_config


@patch.dict('os.environ', {}, clear=True)
class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_config_file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        # Clean up temp config file
        if self.test_config_file:
            self.test_config_file.close()

    def test_resolve_returns_none_when_config_file_missing(self):
        self.assertIsNone(_resolve_config(section=None, config_search_paths=[]))

    def test_resolve_section_in_config_file(self):
        _write_config(self.test_config_file,
        """
        [Section1]
        server = https://qlattice.abzu.ai
        qlattice = section1
        api_token = section1-token

        [Section2]
        server = https://qlattice.abzu.ai
        qlattice = section2
        api_token = section2-token
        """)

        config = _resolve_config(section="Section2",
                                 config_search_paths=[self.test_config_file.name])

        self.assertEqual(config.server, "https://qlattice.abzu.ai")
        self.assertEqual(config.qlattice, "section2")
        self.assertEqual(config.api_token, "section2-token")

    def test_resolve_when_section_not_specified_uses_first_section_in_config(self):
        _write_config(self.test_config_file,
        """
        [Section1]
        server = https://qlattice.abzu.ai
        qlattice = section1
        api_token = section1-token

        [Section2]
        server = https://qlattice.abzu.ai
        qlattice = section2
        api_token = section2-token
        """)

        config = _resolve_config(section=None,
                                 config_search_paths=[self.test_config_file.name])

        self.assertEqual(config.server, "https://qlattice.abzu.ai")
        self.assertEqual(config.qlattice, "section1")
        self.assertEqual(config.api_token, "section1-token")

    def test_resolve_raises_when_config_file_missing(self):
        # It is a temporary file that will be deleted upon close
        self.test_config_file.close()

        with self.assertRaises(FileNotFoundError) as ctx:
            _resolve_config(section="Section1",
                            config_search_paths=[self.test_config_file.name])

        # Ensure we tell the user which files we have looked for.
        self.assertRegex(str(ctx.exception), self.test_config_file.name)

    def test_resolve_raises_when_specified_section_missing(self):
        _write_config(self.test_config_file,
        """
        [Section1]
        server = https://qlattice.abzu.ai
        qlattice = section1
        api_token = section1-token
        """)

        with self.assertRaisesRegex(ValueError, "NonExistingSection"):
            _resolve_config(section="NonExistingSection",
                            config_search_paths=[self.test_config_file.name])

    def test_resolve_raises_when_section_is_malformatted(self):
        _write_config(self.test_config_file,
        """
        [MissingQLattice]
        server = https://qlattice.abzu.ai
        api_token = mouse-token
        """)

        with self.assertRaisesRegex(ValueError, "qlattice"):
            _resolve_config("MissingQLattice",
                            config_search_paths=[self.test_config_file.name])

    def test_resolve_raises_when_multiple_configuration_files_found(self):
        self.test_config_file.close()

        # Emulate that both an rc and .ini file is found
        rc_file = tempfile.NamedTemporaryFile()
        ini_file = tempfile.NamedTemporaryFile()

        _write_config(rc_file,
        """
        [Section1]
        server = https://qlattice.abzu.ai
        qlattice = section1
        api_token = section1-token
        """)

        _write_config(ini_file,
        """
        [Section1]
        server = https://qlattice.abzu.ai
        qlattice = section1
        api_token = section1-token
        """)

        with self.assertRaisesRegex(ValueError, "Multiple configuration files"):
            _resolve_config("Section1",
                            config_search_paths=[rc_file.name,
                                                 ini_file.name]
            )


def _write_config(file, cfg: str):
    file.write(cfg.encode())
    file.seek(0)
