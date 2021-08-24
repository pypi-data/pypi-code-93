from setuptools import setup, find_packages
import codecs
import os


VERSION = '1.0'
DESCRIPTION = 'ETL jobs to collects data from different source db to datawarehouse.'
LONG_DESCRIPTION = 'ETL jobs to collects data from different source db to datawarehouse.'

# Setting up
setup(
    name="py-etl",
    version=VERSION,
    author="Md. Imrul Hasan",
    author_email="imrulhasan273@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['sqlalchemy','pandas','schedule','requests'],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)