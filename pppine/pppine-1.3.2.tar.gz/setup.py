import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_requires = [
    "setuptools>=42",
    "wheel",
    "python-magic",
    "pytz",
    "shortuuid",
    "phonenumbers",
    "pymongo",
]

setuptools.setup(
    name="pppine",
    version="1.3.2",
    author="Mark Kopani",
    author_email="mkopani@gmail.com",
    description="A collection of miscellaneous functions and utilities for Python and/or Django.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mkopani/pppine",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    python_requires=">=3.6",
)
