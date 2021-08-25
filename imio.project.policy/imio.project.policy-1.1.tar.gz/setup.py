# -*- coding: utf-8 -*-
"""Installer for the imio.project.policy package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='imio.project.policy',
    version='1.1',
    description="Policy for project environment",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Stephan Geulette',
    author_email='support@imio.be',
    url='https://pypi.python.org/pypi/imio.project.policy',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['imio', 'imio.project'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Plone',
        'Products.ZNagios',
        'collective.iconifieddocumentactions',
        'collective.monitor',
        'collective.usernamelogger',
        'five.z2monitor',
        'imio.project.pst',
        'setuptools',
        'zc.z3monitor'
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
