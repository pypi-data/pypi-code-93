import os
import shutil
import unittest
import tempfile

from pyrpkg import spec
from pyrpkg.errors import rpkgError


class SpecFileTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = tempfile.mkdtemp(prefix='rpkg-tests.')
        self.specfile = os.path.join(self.workdir, self._testMethodName)

        # Write common header
        spec_fd = open(self.specfile, "w")
        spec_fd.write(
            "Name: test-spec\n"
            "Version: 0.0.1\n"
            "Release: 1\n"
            "Summary: test specfile\n"
            "License: BSD\n"
            "\n"
            "%description\n"
            "foo\n"
            "\n")
        spec_fd.close()

    def tearDown(self):
        shutil.rmtree(self.workdir)
        return

    def test_parse(self):
        # Write some sources
        spec_fd = open(self.specfile, "a")
        spec_fd.write(
            "Source0: https://example.com/tarball.tar.gz\n"
            "Source1: https://example.com/subdir/LICENSE.txt\n"
            "Source2: https://another.domain.com/source.tar.gz\n")
        spec_fd.close()

        s = spec.SpecFile(self.specfile)
        actual = s.sources
        expected = ["tarball.tar.gz", "LICENSE.txt", "source.tar.gz"]
        self.assertEqual(len(actual), len(expected))
        self.assertTrue(all([a == b for a, b in zip(actual, expected)]))

    def test_invalid_specfile(self):
        # Overwrite the specfile, removing mandatory fields
        # Parsing such invalid specfile fails
        spec_fd = open(self.specfile, "w")
        spec_fd.write("Foo: Bar\n")
        spec_fd.close()

        self.assertRaises(rpkgError, spec.SpecFile, [self.specfile])
