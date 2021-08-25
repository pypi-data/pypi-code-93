import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
      'numpy',
      'pandas'
]

setuptools.setup(
    name="KNMI14ext",          # This is the name of the package
    version="1.0.3",                        # The initial release version
    author="X TIAN",                     # Full name of the author
    author_email='xin.tian@kwrwater.nl',
    description="Extraction KNMI14 test",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    # packages=setuptools.find_packages(exclude=['tests*']),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.7',                # Minimum version requirement of the package
    packages=['KNMI14ext'],
    # py_modules=["extract_KNMI14_install"],             # Name of the python package
    # package_dir={'':'./extract_KNMI14_install/src'},     # Directory of the source code of the package
    # package_dir = {'': os.path.join('extract_KNMI14_install', 'scr')},
    install_requires=INSTALL_REQUIRES,                   # Install other dependencies if any
    include_package_data=True,

    # url
)

