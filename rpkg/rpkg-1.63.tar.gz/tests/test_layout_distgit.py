import os
import unittest

from pyrpkg import errors
from pyrpkg.layout import layouts

fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')


class DistGitLayoutTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = os.path.join(fixtures_dir, 'layouts/dist-git')
        self.layout = layouts.DistGitLayout.from_path(self.workdir, None)

    def test_layout_data(self):
        self.assertEqual(self.layout.sourcedir, self.workdir)
        self.assertEqual(self.layout.specdir, self.workdir)
        self.assertEqual(self.layout.root_dir, self.workdir)
        self.assertEqual(self.layout.builddir, self.workdir)
        self.assertEqual(self.layout.rpmdir, self.workdir)
        self.assertEqual(self.layout.rpmfilename,
                         '%%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm')
        self.assertEqual(self.layout.srcrpmdir, self.workdir)
        self.assertEqual(self.layout.sources_file_template, 'sources')

    def test_layout_retired(self):
        self.assertEqual(None, self.layout.is_retired())


class DistGitLayoutErrorsTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = os.path.join(fixtures_dir, 'layouts')

    def test_path_error(self):
        with self.assertRaises(errors.LayoutError) as e:
            layouts.DistGitLayout.from_path(os.path.join(self.workdir, 'notfound'))
        self.assertEqual('package path does not exist', e.exception.args[0])

    def test_specless_error(self):
        with self.assertRaises(errors.LayoutError) as e:
            layouts.DistGitLayout.from_path(os.path.join(self.workdir, 'specless'))
        self.assertEqual('spec file not found.', e.exception.args[0])

    def test_resultsdirhint_error(self):
        with self.assertRaises(errors.LayoutError) as e:
            layouts.DistGitLayout.from_path(os.path.join(self.workdir, 'dist-git'), 'resultsdir')
        self.assertEqual('resultsdir hint given', e.exception.args[0])
