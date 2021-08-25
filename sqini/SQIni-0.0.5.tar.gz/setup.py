import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()
VERSION = '0.0.5'
DESCRIPTION = 'connect table settings of a sqlite database with a ini file for better editing '

# Setting up
setup(
    name="SQIni",
    version=VERSION,
    author="Miku",
    license='MIT',
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/princessmiku/SQIni',
    install_requires=[],
    keywords=['python', 'sqlite3', 'sqlite', 'ini', 'sqini', 'orm', 'database'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
    packages=["sqini"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
        ]
    },
)