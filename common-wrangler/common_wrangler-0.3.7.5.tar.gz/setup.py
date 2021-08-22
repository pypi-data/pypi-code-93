# -*- coding: utf-8 -*-
"""
common_wrangler
Scripts for file and data manipulation, as well as common scripts used in this project as well as
    gaussian_wrangler, ligninkmc, and md_wrangler
"""
from setuptools import setup
import versioneer

DOCLINES = __doc__.split("\n")

setup(
    # Self-descriptive entries which should always be present
    name='common_wrangler',
    author='Heather B Mayes',
    author_email='hmayes@hmayes.com',
    # url='http://www.my_package.com',  # Website
    description=DOCLINES[0],
    long_description="\n".join(DOCLINES[2:]),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='MIT',

    # Which Python importable modules should be included when your package is installed
    packages=['common_wrangler'],

    # Optional include package data to ship with your package
    # Comment out this line to prevent the files from being packaged with your software
    # Extend/modify the list to include/exclude other items as need be
    package_data={'common_wrangler': ["data/*.dat"]
                  },

    entry_points={'console_scripts': ['rename_files = common_wrangler.rename_files:main',
                                      'add2dict = common_wrangler.add2dict:main',
                                      'fill_tpl = common_wrangler.fill_tpl:main'
                                      ],
                  },     package_dir={'common_wrangler': 'common_wrangler'},

    test_suite='tests',
    # Required packages, pulls from pip if needed; do not use for Conda deployment
    install_requires=['numpy', 'six', 'matplotlib'],

    platforms=['Linux',
               'Mac OS-X',
               'Unix',
               'Windows'],            # Valid platforms your code works on, adjust to your flavor
    python_requires=">=3.5",          # Python version restrictions

    # Manual control if final package is compressible or not, set False to prevent the .egg from being made
    # zip_safe=False,

)
