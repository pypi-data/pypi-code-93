from setuptools import setup, find_packages

VERSION = '3.0.0'
DESCRIPTION = 'A python package for parsing prettytable strings'
LONG_DESCRIPTION = 'A python package for parsing prettytable strings. Parse the string into dictionary.'


# Setting up
setup(
    name="parse_prettytable",
    version=VERSION,
    author="Kevin Zhang, Nana Zhan",
    author_email="hr.zhang@gatech.edu",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'prettytable', 'parse'],
    classifiers=[
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
