import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="comtrade",
    version="0.0.6",
    author="David Parrini",
    author_email="d.parrini@gmail.com",
    description="A module designed to read Common Format for Transient "
                "Data Exchange (COMTRADE) file format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dparrini/python-comtrade",
    packages=setuptools.find_packages(),
    py_modules=["comtrade"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)