import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ipey",                     # This is the name of the package
    version="0.0.3",                        # The initial release version
    author="Markus Wallinger",                     # Full name of the author
    license='MIT',
    description="Create IPE drawings in python",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["ipey"],             # Name of the python package
    packages=setuptools.find_packages("src"),
    package_dir={'':'src'},     # Directory of the source code of the package
    install_requires=[],                     # Install other dependencies if any
    package_data={'': ['static/settings.ini', 'static/basic.xml', 'License.txt']},
    #include_package_data=True
)