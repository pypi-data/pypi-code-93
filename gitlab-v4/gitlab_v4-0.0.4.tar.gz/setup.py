import codecs
import os.path
import re
from setuptools import setup


# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))


def load(filename):
    # use utf-8 if this throws up an error
    return open(filename, "rb").read().decode("utf-8")


def read(*parts):
    return codecs.open(os.path.join(HERE, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="gitlab_v4",
    version=find_version("gitlab_client", "__init__.py"),
    description="Wrapper for Gitlab API v4",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/abhaykoduru/gitlab_client",
    author="Abhay Santhosh Koduru",
    author_email="k.abhaysanthosh@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    packages=["gitlab_client"],
    include_package_data=True,
    install_requires=load("requirements.txt")
)
