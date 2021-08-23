#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

readme_file = os.path.join(here, 'README.md')
if os.path.exists(readme_file):
    with open(readme_file, encoding='UTF-8') as f:
        long_description = f.read()
else:
    long_description = "Some commonly used modules for personal use."

require_file = os.path.join(here, "requirements.txt")
if os.path.exists(require_file):
    with open(require_file, encoding='UTF-8') as f:
        install_requires = f.read().split("\n")
else:
    install_requires = []

setuptools.setup(
    name='user_tools',
    version='0.0.12',
    description='Some commonly used modules for personal use.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='SkypeKey',
    author_email='enablekey@outlook.com',
    url='https://github.com/Skypekey/user_tools',
    project_urls={
        'Documentation': 'https://github.com/Skypekey/user_tools/wiki',
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/Skypekey/user_tools',
        'Tracker': 'https://github.com/Skypekey/user_tools/issues',
    },
    license='GNU GPLv3',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3',
    ],
    keywords='time file json',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    python_requires='>=3.8',

    # If some data files are used in the module, and file in module directory.
    # the following options should be used.
    # package_data={
    #     'package_name': ['package_data.dat'],
    # },
    # If some data files are used in the module,
    # the file not in module directory.
    # the following options should be used.
    # data_files=[('data_directory', ['data/data_file'])],

    # If using MANIFEST.in files to find data files.
    # you must use the following options.
    # include_package_data=True,

    # If your package has a main function,
    # which must be executed from the specified module,
    # you must use the following options.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },

    # The following are optional parameters,
    # generally do not need to be used.
    # py_modules=[],
    # scripts=['scripts/xmlproc_parse', 'scripts/xmlproc_val'],
)
