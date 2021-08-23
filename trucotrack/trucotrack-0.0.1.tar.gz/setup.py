import os
import pathlib
from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Generate data files from captured motion'
HERE = pathlib.Path(__file__).parent
LONG_DESCRIPTION = (HERE / "README.md").read_text()

setup(
    name='trucotrack',
    version=VERSION,
    author='Carlos Capote Pérez-Andreu',
    author_email='<carlos.capote@hawara.es>',
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['mediapipe', 'opencv-python'],
    entry_points={
        'console_scripts': [
            'trucotrack=trucotrack.cli:main',
        ]
    },
    keywords=['python', 'motion', 'motion capture', 'video',
        'stream', 'video stream', 'camera stream'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows'])
