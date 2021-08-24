#!/usr/bin/env python3

"""Installateur"""

from setuptools import setup, find_packages
import codecs
import os

import sys

def readme():
    """Lecture du README"""
    with codecs.open("README.md", encoding="utf8", errors="replace") as file:
        return file.read()

datadir = os.path.join('pyromaths','qt', 'data')
datafiles = [(d, [os.path.join(d,f) for f in files])
    for d, folders, files in os.walk(datadir)]

# Chargement des variables VERSION, COPYRIGHT_YEAR
# Ceci n'est pas fait par un `import pyromaths.version` pour ne pas importer
# des dependances qui ne sont pas encore installees.
with codecs.open("pyromaths/qt/version.py", encoding="utf8", errors="replace") as file:
    exec(compile(file.read(), "version.py", "exec"))

def _mac_opt():
    '''MacOS: py2app helps generate a self-contained app.'''
    plist = dict(CFBundleIdentifier  = "org.pyromaths.pyromaths",
                 CFBundleName        = "Pyromaths",
                 CFBundleDisplayName = "Pyromaths",
                 CFBundleVersion     = VERSION,
                 CFBundleShortVersionString = VERSION,
                 NSHumanReadableCopyright = u"© Jérôme Ortais",
                 CFBundleDevelopmentRegion = "French",
                 CFBundleIconFile    = "pyromaths",
                 CFBundleExecutable  = "pyromaths",
                 CFBundlePackageType = "APPL",
                 CFBundleSignature   = "PYTS",
                 )
    # Unused Qt libraries/frameworks
    lib_dynload_unused = ['_asyncio','_decimal','_sha256', '_bisect', '_elementtree', '_sha3',
     '_blake2', '_hashlib', '_ssl', '_bz2', '_heapq', '_uuid', '_codecs_cn', '_lzma', 'array',
     '_codecs_hk', '_md5', 'grp', '_codecs_iso2022', '_multibytecodec', 'mmap', '_codecs_jp',
     '_multiprocessing', 'resource', '_codecs_kr', '_opcode', 'sip', '_codecs_tw', '_pickle',
     '_datetime', '_queue']
    site_packages_unused = ['asyncio',]
    excludes = lib_dynload_unused + site_packages_unused
    # py2app
    py2app = dict(plist    = plist,
                  iconfile = 'data/macos/pyromaths.icns',
                  packages=find_packages(),
                  includes=['asyncio', 'concurrent', 'jinja2', 'markupsafe', 'simplejson', 'fractions'],
                  excludes = excludes,
                  )
    return dict(
        app        = ['data/macos/pyromaths-qt.py'],
        data_files = [
            ( 'data', ['data/macos/qtbase_fr.qm']),
        ] ,
        options    = {'py2app': py2app},
    )

# Set platform-specific options
if "py2app" in sys.argv:
    options = _mac_opt()
    setup(
        **options
    )
else:
    setup(
        name="pyromaths-qt",
        version=VERSION,
        packages=find_packages(exclude=["tests*"]),
        namespace_packages=["pyromaths"],
        install_requires=["lxml>=4.2.1", "pyromaths>=18.7", "PyQt5>=5.10"],
        include_package_data=True,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description="Create maths exercises in LaTeX and PDF format -- QT client",
        url="http://www.pyromaths.org",
        download_url="http://www.pyromaths.org/telecharger/",
        license="GPLv2",
        entry_points={
            "gui_scripts": ["pyromaths-qt = pyromaths.qt.__main__:main"],
        },
        keywords="exercices math latex school",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Education",
            "Environment :: X11 Applications :: Qt",
            "Environment :: MacOS X",
            "Environment :: Win32 (MS Windows)",
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Topic :: Software Development :: Code Generators",
            "Topic :: Text Processing :: Markup :: LaTeX",
        ],
        long_description=readme(),
        long_description_content_type="text/markdown",
        data_files = datafiles,
        zip_safe=False,
        project_urls={
            "Documentation": "http://pyromaths.readthedocs.org",
            "Download": "https://www.pyromaths.org/telecharger/",
            "Forum": "https://forum.pyromaths.org",
            "Sources": "https://framagit.org/pyromaths/pyromaths",
            "Tickets": "https://framagit.org/pyromaths/pyromaths/issues",
            "Version en ligne": "http://enligne.pyromaths.org/",
        },
    )

# Post-processing
if "py2app" in sys.argv:
    # py2app/setenv hack: replace executable with one appending several LaTeX
    # distributions locations to the path.
    mactex   = "/Library/TeX/texbin:/usr/texbin:/usr/local/bin"
    macports = "/opt/local/bin:/opt/local/sbin"
    fink     = "/sw/bin"
    path     = "%s:%s:%s" % (mactex, macports, fink)
    f = open('dist/Pyromaths.app/Contents/MacOS/setenv.sh', 'w')
    f.write('''#!/bin/sh
PWD=$(dirname "$0"); /usr/bin/env PATH="$PATH:%s" $PWD/pyromaths''' % path)
    os.system("chmod +x dist/Pyromaths.app/Contents/MacOS/setenv.sh")
    os.system("sed -i '' '10s/pyromaths/setenv.sh/' dist/Pyromaths.app/Contents/Info.plist")
