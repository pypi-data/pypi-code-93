import setuptools
import re
import ast


with open("README.md", "r") as fh:
    long_description = fh.read()

version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('stackifyapm/__init__.py') as f:
    f = f.read()
    version = ast.literal_eval(version_re.search(f).group(1))

setuptools.setup(
    name="stackify-python-apm",
    version=version,
    author="Stackify",
    author_email="support@stackify.com",
    description="This is the official Python module for Stackify Python APM.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.stackify.com",
    packages=setuptools.find_packages(),
    zip_safe=True,
    install_requires=[
        "blinker>=1.1",
        "protobuf>=3.9.1",
        "requests>=2.21.0",
        "retrying>=1.2.3",
        "stackify-api-python>=1.0.5"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
)
