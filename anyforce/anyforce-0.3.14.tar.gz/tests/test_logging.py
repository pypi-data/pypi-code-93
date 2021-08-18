# -*- coding: utf-8 -*-

import unittest

from anyforce import logging


class TestLogging(unittest.TestCase):
    def test_logging(self):
        logging.getLogger("test").with_field(k="v").debug("debug")
        logging.getLogger("test").with_field(k="v").info("info")
        logging.getLogger("test").with_field(k="v").warning("warning")
        logging.getLogger("test").with_field(k="v").success("success")
        logging.getLogger("test").with_field(k="v").log(logging.INFO, "info")
