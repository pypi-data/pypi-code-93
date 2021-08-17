import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AmiAutomation", 
    version="0.1.2", ### Change before commit
    author="AMI",
    author_email="luis.castro@amiautomation.com",
    description="Package to extract binary files into pandas dataframes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
    python_requires='>=3.6',
    data_files=[('DLLs\\',["Kernel.Message.dll","DigitArcPX3.Tools.DataToPython.dll","ICSharpCode.SharpZipLib.dll"])],
    install_requires=['pandas>=1.1.0'],
    )

    ##   https://packaging.python.org/tutorials/packaging-projects/
    #python setup.py sdist bdist_wheel
    #twine upload dist/*
