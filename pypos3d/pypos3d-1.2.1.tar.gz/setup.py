# -*- coding: utf-8 -*-
'''
Created on 4 oct. 2020
Setup of library delivery
'''
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pypos3d", # Replace with your own username
    version="1.2.1",
    author="Olivier Dufailly",
    author_email="dufgrinder@laposte.net",
    description="Wavefront files and Poser files manipulation library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://sourceforge.net/projects/pojamas",
    
    package_dir={'': 'src'},  
    packages=setuptools.find_packages(where='src', include=('pypos3d', 'pypos3d.*', 'langutil' )),

    #include_package_data=True,
    #package_data={ 'pypos3d':[ '../CHANGELOG.md', '../LICENSE'], },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy>=1.19', 'scipy>=1.5', 'xlrd>=1.2'],
    python_requires='>=3.6',
)
