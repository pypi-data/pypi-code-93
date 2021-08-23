import os
import unittest

from pyrpkg import errors
from pyrpkg.layout import layouts

fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')


class SRPMLayoutTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = os.path.join(fixtures_dir, 'layouts/srpm')
        self.layout = layouts.SRPMLayout.from_path(self.workdir)

    def test_layout_data(self):
        self.assertEqual(self.layout.sourcedir, os.path.join(self.workdir, 'SOURCES'))
        self.assertEqual(self.layout.specdir, os.path.join(self.workdir, 'SPECS'))
        self.assertEqual(self.layout.root_dir, self.workdir)
        self.assertEqual(self.layout.builddir, os.path.join(self.workdir, 'BUILD'))
        self.assertEqual(self.layout.rpmdir, os.path.join(self.workdir, 'RPMS'))
        self.assertEqual(self.layout.rpmfilename,
                         '%%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm')
        self.assertEqual(self.layout.srcrpmdir, os.path.join(self.workdir, 'SRPMS'))
        self.assertEqual(self.layout.sources_file_template, '.{0.repo_name}.metadata')

    def test_layout_retired(self):
        self.assertEqual(None, self.layout.is_retired())


class SRPMLayoutErrorsTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = os.path.join(fixtures_dir, 'layouts')

    def test_path_error(self):
        with self.assertRaises(errors.LayoutError) as e:
            layouts.SRPMLayout.from_path(os.path.join(self.workdir, 'notfound'))
        self.assertEqual('package path does not exist', e.exception.args[0])

    def test_specless_error(self):
        with self.assertRaises(errors.LayoutError) as e:
            layouts.SRPMLayout.from_path(os.path.join(self.workdir, 'srpm-specless'))
        self.assertEqual('spec file not found.', e.exception.args[0])
