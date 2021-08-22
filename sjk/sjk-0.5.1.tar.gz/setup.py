from setuptools import setup, find_packages
from os import path, walk

########################################################################
# BASIC PACKAGE METADATA
########################################################################

sargs = dict(

    name             = 'sjk',
    version          = '0.5.1',
    description      = 'SJK: Some Jupyter Kernels.',
    author           = 'Roi Docampo',
    url              = 'https://github.com/roidocampo/sjk',
    license          = 'MIT',
    install_requires = [ 'ipykernel' ],
    python_requires  = ">=3.5",

)

########################################################################
# LONG DESCRIPTION
########################################################################

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    sargs['long_description'] = f.read()
    sargs['long_description_content_type'] = 'text/x-rst'

########################################################################
# CLASSIFIERS
########################################################################

classifiers = """\

Development Status :: 4 - Beta
Framework :: Jupyter
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Programming Language :: Python :: 3
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Topic :: Scientific/Engineering
Topic :: Software Development

"""

sargs['classifiers'] = [ c for c in classifiers.split("\n") if c ]

########################################################################
# PYTHON MODULES
########################################################################

sargs['packages'] = find_packages()

########################################################################
# DATA FILES
########################################################################

def data_files(src_root, dest_root):
    data = []
    src_len = len(src_root)
    for src_dir, subdirs, files in walk(src_root):
        if files:
            rel_dir = src_dir[src_len:]
            dest_dir = dest_root + rel_dir
            files = [ path.join(src_dir, f) for f in files ]
            data.append((dest_dir, files))
    return data

sargs['data_files'] = data_files('kernelspecs', 'share/jupyter/kernels')

########################################################################
# RUN SETUP
########################################################################

setup(**sargs)
