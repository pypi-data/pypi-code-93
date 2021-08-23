import os
import unittest

from pyrpkg import errors
from pyrpkg.layout import layouts

fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')


class DistGitResultsDirLayoutTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = os.path.join(fixtures_dir, 'layouts/dist-git')
        self.layout = layouts.DistGitResultsDirLayout.from_path(self.workdir, 'resultsdir')

    def test_layout_data(self):
        self.assertEqual(self.layout.sourcedir, self.workdir)
        self.assertEqual(self.layout.specdir, self.workdir)
        self.assertEqual(self.layout.root_dir, self.workdir)
        self.assertEqual(self.layout.builddir, os.path.join(self.workdir, 'results'))
        self.assertEqual(self.layout.rpmdir, os.path.join(self.workdir, 'results'))
        self.assertEqual(self.layout.rpmfilename, '%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm')
        self.assertEqual(self.layout.srcrpmdir, os.path.join(self.workdir, 'results'))
        self.assertEqual(self.layout.sources_file_template, 'sources')

    def test_layout_retired(self):
        self.assertEqual(None, self.layout.is_retired())


class DistGitResultsDirLayoutErrorsTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = os.path.join(fixtures_dir, 'layouts')

    def test_path_error(self):
        with self.assertRaises(errors.LayoutError) as e:
            layouts.DistGitResultsDirLayout.from_path(os.path.join(self.workdir, 'notfound'))
        self.assertEqual('package path does not exist', e.exception.args[0])

    def test_specless_error(self):
        with self.assertRaises(errors.LayoutError) as e:
            layouts.DistGitResultsDirLayout.from_path(os.path.join(self.workdir, 'specless'))
        self.assertEqual('spec file not found.', e.exception.args[0])

    def test_wronghint_error(self):
        with self.assertRaises(errors.LayoutError) as e:
            layouts.DistGitResultsDirLayout.from_path(os.path.join(self.workdir, 'dist-git'),
                                                      'wronghint')
        self.assertEqual('resultsdir hint not given', e.exception.args[0])
