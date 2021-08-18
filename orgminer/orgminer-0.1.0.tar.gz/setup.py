import sys
import setuptools

if sys.argv[-1] == "setup.py":
    print('To start installation, run \n\tpython setup.py install\n')

py_ver = sys.version_info[:2]

if py_ver < (3, 7):
    sys.stderr.write(
        f"""
        This package requires Python 3.7+.
        You have Python {py_ver[0]}.{py_ver[1]}.\n
        """
    )
    sys.exit(1)

# Meta data to be displayed on PyPI
author          = 'Jing (Roy) Yang'
author_email    = 'roy.j.yang@qut.edu.au'
description     = '[LEGACY] Python toolkit for organizational mining, now maintained as "OrdinoR"'
url             = 'https://github.com/roy-jingyang/OrgMiner'
project_url     = {
    'Documentation': 'https://ordinor.readthedocs.io',
    'Source': 'https://github.com/roy-jingyang/OrdinoR',
    'Tracker': 'https://github.com/roy-jingyang/OrdinoR/issues'
}
classifier      = [
    'Development Status :: 7 - Inactive',
    'Programming Language :: Python',
    'License :: OSI Approved :: GNU GPLv3',
    'Operating System :: OS Independent'
]

# Package information
name                = 'orgminer'
version             = '0.1.0'
python_requires     = '>=3.7'

packages            = [
    'orgminer'
]

install_requires    = [
    'ordinor'
]

if __name__ == '__main__':
    setuptools.setup(
        author=author,
        author_email=author_email,
        description=description,
        url=url,
        project_url=project_url,
        classifier=classifier,

        name=name,
        version=version,
        python_requires=python_requires,
        install_requires=install_requires,
        packages=packages,
    )
