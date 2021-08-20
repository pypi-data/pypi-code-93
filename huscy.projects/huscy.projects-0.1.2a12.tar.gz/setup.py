from os import path

from setuptools import find_namespace_packages, setup

from huscy.projects import __version__


with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

extras_require = {
    'development': [
        'psycopg2-binary',
    ],
    'testing': [
        'tox',
        'watchdog',
    ],
}

install_requires = [
    'Django>=2.2',
    'djangorestframework>=3.10',
    'django-guardian>=1.4',
    'drf-nested-routers>=0.90',
]


setup(
    name='huscy.projects',
    version=__version__,
    license='AGPLv3+',

    author='Alexander Tyapkov, Mathias Goldau, Stefan Bunde',
    author_email='tyapkov@gmail.com, goldau@cbs.mpg.de, stefanbunde+git@posteo.de',

    packages=find_namespace_packages(),

    install_requires=install_requires,
    extras_require=extras_require,

    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://huscy.org',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
    ],
)
