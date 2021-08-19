import setuptools
import codecs
import os.path


def read(rel_path):
   here = os.path.abspath(os.path.dirname(__file__))
   with codecs.open(os.path.join(here, rel_path), 'r') as fp:
      return fp.read()


def get_version(rel_path):
   for line in read(rel_path).splitlines():
      if line.startswith('VERSION'):
         delim = '"' if '"' in line else "'"
         return line.split(delim)[1]
   else:
      raise RuntimeError("Unable to find version string.")


with open('requirements.txt') as f:
   required = f.read().splitlines()

with open("README.md", "r") as fh:
   long_description = fh.read()

setuptools.setup(
    name="warden-sdk",
    version=get_version("warden_sdk/consts.py"),
    author="Ferant Inc",
    author_email="mpodsiadly@hawk.iit.edu",
    description="Python client for Ferant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/theferant/warden",
    packages=setuptools.find_packages(exclude=("tests", "tests.*")),
    # PEP 561
    package_data={"warden_sdk": ["py.typed"]},
    include_package_data=True,
    install_requires=[
        'certifi>=2021.5.30', 'chardet>=4.0.0', 'filelock>=3.0.12',
        'idna>=2.10', 'requests>=2.25.1', 'requests-file>=1.5.1', 'six>=1.16.0',
        'tldextract>=3.1.0', 'urllib3>=1.26.6'
    ],
    extras_require={"flask": ["flask>=0.11", "blinker>=1.1"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    options={"bdist_wheel": {
        "universal": "1"
    }},
    python_requires='>=3.6')
