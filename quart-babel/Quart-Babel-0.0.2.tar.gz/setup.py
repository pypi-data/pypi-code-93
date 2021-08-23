
from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), 'rb') as f:
    long_description = f.read().decode('utf-8')


setup(
    name='Quart-Babel',
    version='0.0.2',
    url='https://github.com/crood58/quart-babel',
    license='BSD',
    author='Chris Rood',
    author_email='crood58@gmail.com',
    maintainer='Chris Rood',
    maintainer_email='crood58@gmail.com',
    description='Adds i18n/l10n support to Quart applications',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['quart_babel'],
    zip_safe=False,
    install_requires=[
        'pytz',
        'Quart',
        'Babel>=2.3',
        'Jinja2>=3.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-mock',
            'bumpversion',
            'ghp-import',
            'sphinx',
            'Pallets-Sphinx-Themes'
        ]
    }
)