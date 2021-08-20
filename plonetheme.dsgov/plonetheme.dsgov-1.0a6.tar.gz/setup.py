# -*- coding: utf-8 -*-
"""Installer for the plonetheme.dsgov package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='plonetheme.dsgov',
    version='1.0a6',
    description=u"O Design System do Governo Federal",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone CMS',
    author='Fabio Santos',
    author_email='f4bio.sa@gmail.com',
    url='https://github.com/f4biosa/plonetheme.dsgov',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/plonetheme.dsgov',
        'Source': 'https://github.com/f4biosa/plonetheme.dsgov',
        'Tracker': 'https://github.com/f4biosa/plonetheme.dsgov/issues',
        # 'Documentation': 'https://plonetheme.dsgov.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['plonetheme'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires="==2.7, >=3.6",
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'plone.app.themingplugins',
        'collective.themefragments',
        'z3c.jbot',
        'plone.api>=1.8.4',
        'plone.restapi',
        'plone.app.dexterity',
        'plone.app.mosaic',
        'eea.facetednavigation',
        'plone.app.registry',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = plonetheme.dsgov.locales.update:update_locale
    """,
)
