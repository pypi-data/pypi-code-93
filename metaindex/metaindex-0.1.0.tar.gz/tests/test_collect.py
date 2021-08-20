import pathlib
import unittest

from metaindex import configuration
from metaindex.main import collect_files_and_metadata

HERE = pathlib.Path(__file__).resolve().parent
BASEDIR = HERE.parent


class TestCollect(unittest.TestCase):
    def setUp(self):
        self.config = configuration.load(HERE / 'test.conf')

    def test_only_dir(self):
        paths, metadata = collect_files_and_metadata(self.config, [BASEDIR])
        self.assertEqual(len(paths), 1)
        self.assertIn(BASEDIR / ".metadata.json", metadata)

    def test_single_file(self):
        paths, metadata = collect_files_and_metadata(self.config, [BASEDIR / "README.md"])
        self.assertEqual(len(paths), 1)
        self.assertIn(BASEDIR / ".metadata.json", metadata)

    def test_expand_dir(self):
        paths, metadata = collect_files_and_metadata(self.config, [BASEDIR], expand=True)
        self.assertIn(BASEDIR / "README.md", paths)
        self.assertIn(BASEDIR / "setup.py", paths)
        self.assertNotIn(BASEDIR / "metaindex", paths)
        self.assertNotIn(BASEDIR / "metaindex" / "main.py", paths)
        self.assertIn(BASEDIR / ".metadata.json", metadata)

    def test_recursive(self):
        paths, metadata = collect_files_and_metadata(self.config, [BASEDIR], recursive=True)
        self.assertIn(BASEDIR / ".metadata.json", metadata)
        self.assertIn(BASEDIR / "metaindex" / ".metadata.json", metadata)
        self.assertIn(BASEDIR / "tests" / ".metadata.json", metadata)

    def test_expand_recursive(self):
        paths, metadata = collect_files_and_metadata(self.config, [BASEDIR], expand=True, recursive=True)
        self.assertIn(BASEDIR / "README.md", paths)
        self.assertIn(BASEDIR / "metaindex" / "main.py", paths)
        self.assertIn(BASEDIR / "tests" / "test_collect.py", paths)

