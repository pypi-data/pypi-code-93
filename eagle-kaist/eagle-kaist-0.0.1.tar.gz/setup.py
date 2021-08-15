import setuptools

def read_desc():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description

def read_requirements():
    with open("requirements.txt") as fh:
        requirements = fh.read()
        requirements = requirements.splitlines()
    return requirements

if __name__ == "__main__":
    setuptools.setup(
        name="eagle-kaist",  # This is the name of the package
        version="0.0.1",  # The initial release version
        author="Thanh Luong",  # Full name of the author
        author_email="sputnikav@gmail.com",
        description="Stock Extractor library",
        long_description=read_desc(),  # Long description read from the the readme file
        long_description_content_type="text/markdown",
        url="",
        packages=setuptools.find_packages(),  # List of all python modules to be installed
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],  # Information to filter the project on PyPi website
        python_requires=">=3.7.6",  # Minimum version requirement of the package
        # package_data={'': ['config.ini']},
        include_package_data=True,
        # py_modules=["eagle"],  # Name of the python package
        # package_dir={"": "eagle/"},  # Directory of the source code of the package
        install_requires=read_requirements(),  # Install other dependencies if any
    )
