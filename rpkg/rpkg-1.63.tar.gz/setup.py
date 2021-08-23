#!/usr/bin/python

import os

from setuptools import find_packages, setup


def read_requirements(requirements_file):
    specifiers = []
    dep_links = []

    def read_lines():
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line == '' or line.startswith('#') or line.startswith('-r'):
                    continue
                yield line

    for line in read_lines():
        if line.startswith('git+'):
            dep_links.append(line)
        else:
            specifiers.append(line)

    return specifiers, dep_links


setup_py_path = os.path.dirname(os.path.realpath(__file__))
pypi_txt = os.path.join(setup_py_path, 'requirements', 'pypi.txt')
test_pypi_txt = os.path.join(setup_py_path, 'requirements', 'test-pypi.txt')

install_requires, dep_links = read_requirements(pypi_txt)
tests_require, test_dep_links = read_requirements(test_pypi_txt)
dep_links += test_dep_links

readme_rst = os.path.join(setup_py_path, 'README.rst')
with open(readme_rst, 'r') as readme:
    long_description = readme.read().rstrip()

setup(
    name="rpkg",
    version="1.63",
    author="Dennis Gilmore",
    author_email="ausil@fedoraproject.org",
    description=("A python library and runtime script for managing RPM"
                 "package sources in a git repository"),
    long_description=long_description,
    license="GPLv2+",
    url="https://pagure.io/rpkg",
    packages=find_packages(),
    setup_requires=['setuptools_scm', 'pytest-runner'],
    install_requires=install_requires,
    tests_require=tests_require,
    dependency_links=dep_links,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
