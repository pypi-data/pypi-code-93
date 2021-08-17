from setuptools import find_namespace_packages, setup

from huscy.bookings import __version__


extras_require = {
    'development': [
        'psycopg2-binary',
    ],
    "testing": [
        "tox",
        "watchdog",
    ],
}

install_requires = [
    'huscy.appointments',
    'huscy.projects',
]


setup(
    name="huscy.bookings",
    version=__version__,
    license='AGPLv3+',

    author='Alexander Tyapkov, Mathias Goldau, Stefan Bunde',
    author_email='tyapkov@gmail.com, goldau@cbs.mpg.de, stefanbunde+git@posteo.de',

    packages=find_namespace_packages(),

    install_requires=install_requires,
    extras_require=extras_require,

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
