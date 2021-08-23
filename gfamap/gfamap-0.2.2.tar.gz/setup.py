from setuptools import setup, find_packages

VERSION = '0.2.2'
DESCRIPTION = 'Map edges of a genome graph to a reference genome database.'

setup(
    name = 'gfamap',
    version = VERSION,
    author = 'Joseph Lee',
    author_email = 'joseph.lee@u.nus.edu',
    url = 'https://github.com/jleechung/gfamap',
    description = DESCRIPTION,
    long_description = DESCRIPTION,
    license = 'MIT',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'gfamap = gfamap.gfamap:main'
            ]
        },
    keywords = 'python genome graph genome assembly'
)

