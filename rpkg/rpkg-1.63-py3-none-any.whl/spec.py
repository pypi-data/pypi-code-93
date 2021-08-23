# spec.py - Simple specfile parser that finds source file names
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import re
import subprocess

from pyrpkg.errors import rpkgError


class SpecFile(object):
    """Simple specfile parser that finds source file names"""

    sourcefile_expression = re.compile(r'^source[0-9]*:\s*(?P<val>.*)\s*$', re.IGNORECASE)

    def __init__(self, spec):
        self.spec = spec
        self.sources = []

        self.parse()

    def parse(self):
        """Call rpmspec and find source tags from the result."""
        stdout = run(self.spec)
        for line in stdout.splitlines():
            m = self.sourcefile_expression.match(line)
            if not m:
                continue

            # Forget domain and path, only store file name
            val = m.group('val').split('/')[-1]
            self.sources.append(val)


def run(spec):
    cmdline = ['rpmspec', '-P', spec]
    try:
        process = subprocess.Popen(cmdline,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input)
    except Exception as e:
        raise rpkgError('Error running rpmspec on "%s": %s' % (spec, e))

    retcode = process.poll()
    if retcode:
        raise rpkgError('Error running rpmspec on "%s", return code %s'
                        % (spec, retcode))

    return stdout.decode('utf-8')
