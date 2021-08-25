# -*- coding: utf-8 -*-
"""Setup module for flask taxonomy."""
import os

from setuptools import setup, find_packages

readme = open('README.md').read()
history = open('CHANGES.md').read()

install_requires = [
]

tests_require = [
    'oarepo-validate'
]

extras_require = {
    'tests': [
        *tests_require,
        'oarepo[tests]'],
    'build': [
        'oarepo-model-builder'
    ]
}

setup_requires = [
    'pytest-runner>=2.7',
]

g = {}
with open(os.path.join('oarepo_invenio_model', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name="oarepo_invenio_model",
    version=version,
    url="https://github.com/oarepo/invenio_oarepo_invenio_model",
    license="MIT",
    author="Miroslav Simek",
    author_email="miroslav.simek@vscht.cz",
    description="Invenio data model for OARepo",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    zip_safe=False,
    packages=['oarepo_invenio_model'],
    entry_points={
        'oarepo_mapping_includes': [
            'oarepo_invenio_model=oarepo_invenio_model.included_mappings'
        ],
        'invenio_jsonschemas.schemas': [
            'oarepo_invenio_model = oarepo_invenio_model.jsonschemas'
        ],
        'oarepo_model_builder.datamodels': [
            'oarepo_invenio_model = oarepo_invenio_model.datamodels'
        ]
    },
    include_package_data=True,
    setup_requires=setup_requires,
    extras_require=extras_require,
    install_requires=install_requires,
    tests_require=tests_require,
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 4 - Beta',
    ],
)
