import os
import re
from os.path import join, dirname
from setuptools import setup, find_packages


def get_version(*file_paths):
    """Retrieves the version from the given path"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def long_description():
    """Return long description from README.md if it's present
    because it doesn't get installed."""
    try:
        return open(join(dirname(__file__), "README.md")).read()
    except IOError:
        return ""


setup(
    name="rh_email_tpl",
    packages=find_packages(exclude=["example*"]),
    version=get_version("rh_email_tpl", "__init__.py"),
    description="Internal RegioHelden tool for building styled html emails",
    author="RegioHelden <entwicklung@regiohelden.de>",
    author_email="entwicklung@regiohelden.de",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    install_requires=[
        "Django>=3.2",
        "premailer>=3.8.0",
    ],
    license="",
    url="",
    download_url="",
    keywords=["django", "emails", "html-email"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
)
