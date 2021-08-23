import os
import unittest

from pyrpkg import errors
from pyrpkg.layout import layouts

fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')


class IncompleteLayoutTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = os.path.join(fixtures_dir, 'layouts/incomplete-package')
        self.layout = layouts.IncompleteLayout.from_path(self.workdir)

    def test_layout_data(self):
        self.assertEqual(self.layout.sourcedir, None)
        self.assertEqual(self.layout.specdir, None)
        self.assertEqual(self.layout.root_dir, self.workdir)
        self.assertEqual(self.layout.builddir, None)
        self.assertEqual(self.layout.rpmdir, None)
        self.assertEqual(self.layout.rpmfilename, None)
        self.assertEqual(self.layout.srcrpmdir, None)
        self.assertEqual(self.layout.sources_file_template, 'sources')

    def test_layout_not_retired(self):
        self.assertEqual(None, self.layout.is_retired())


class IncompleteLayoutErrorsTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = os.path.join(fixtures_dir, 'layouts')

    def test_path_error(self):
        with self.assertRaises(errors.LayoutError) as e:
            layouts.IncompleteLayout.from_path(os.path.join(self.workdir, 'notfound'))
        self.assertEqual('package path does not exist', e.exception.args[0])
