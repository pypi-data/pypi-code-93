# -*- coding: utf-8 -*-
'''
Created on 4 oct. 2020
Setup of Unit Tests delivery
'''
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("coverage_results.txt", "r") as fh:
    long_description += '\n\n\n' + fh.read()

setuptools.setup(
    name="pypos3dtu",
    version="1.2.1",
    author="Olivier Dufailly",
    author_email="dufgrinder@laposte.net",
    description="Unit Tests for Wavefront files and Poser files manipulation library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://sourceforge.net/projects/pojamas",
    
    package_dir={'':'src'},
    packages=setuptools.find_packages(where='src', include=('pypos3dtu', 'pypos3dtu.*') ),
    
    # data_files=[ ('tu/srcdata', [ 'tu/srcdata', ] ), ], --> Deprecated
    # data_files = [ ( '.', [ './tu.sh', 'CHANGELOG.md' ]), ],
    data_files = [ ( '', [ './tu.sh', 'CHANGELOG.md' ]), ],
    # data_files = [ './tu.sh', 'CHANGELOG.md' ], --> Files installed in ~/.local
    include_package_data=True,
    package_data={ 'pypos3dtu' : [ 'pypos3dtu/srcdata/*.*', 'pypos3dtu/../../*.sh'] },
        
    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pypos3d==1.2.1', ],
    python_requires='>=3.6',
)
