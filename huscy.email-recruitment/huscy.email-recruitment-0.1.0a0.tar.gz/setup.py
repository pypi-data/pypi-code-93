from setuptools import find_namespace_packages, setup

from huscy.email_recruitment import __version__


setup(
    name='huscy.email-recruitment',
    version=__version__,
    license='AGPLv3+',

    author='Alexander Tyapkov, Mathias Goldau, Stefan Bunde',
    author_email='tyapkov@cbs.mpg.de, goldau@cbs.mpg.de, stefanbunde+git@posteo.de',

    packages=find_namespace_packages(),

    install_requires=[
        'django>=2.0',
    ],
    extras_require={
        'development': [
            'psycopg2-binary',
        ],
        'testing': [
            'tox',
            'watchdog',
        ],
    },

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
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
    ],
)
