from setuptools import setup
import os
import re
import codecs
# Create new package with python setup.py sdist

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Create new package with python setup.py sdist
setup(
    name='cryoloBM',
    version=find_version("cryoloBM", "__init__.py"),
    python_requires='>3.4.0',
    packages=['cryoloBM','cryoloBM_tools'],
    url='',
    license='MIT',
    author='Thorsten Wagner',
    install_requires=[
        "matplotlib >= 3.4.2",
        #"cryolo >= 1.8.0b32",
        "numpy >= 1.16.0, < 1.19.0",
        "pyStarDB==0.1.0b3",
        "pandas==1.1.4",
        "mrcfile >= 1.0.0,<= 1.1.2",
    ],
    author_email='thorsten.wagner@mpi-dortmund.mpg.de',
    description='Boxmanager to create training data for crYOLO',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'cryolo_boxmanager.py = cryoloBM.boxmanager:run',
            'cryolo_boxmanager_tools.py = cryoloBM.boxmanager_tools:_main_'
        ]},
)
