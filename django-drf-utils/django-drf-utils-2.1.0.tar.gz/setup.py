#!/usr/bin/env python3

from datetime import datetime
from setuptools import setup, find_packages

# 0.0.0-dev.* version identifiers for development only (not public)
__version__ = "0.0.0.dev" + datetime.now().strftime("%Y%m%d")

setup(
    name="django-drf-utils",
    version="2.1.0",
    license="LGPL3",
    description="Utilities for commonly used functionality in django and "
    "django-rest-framework among BIWG projects.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jaroslaw Surkont, "
    "Gerhard Bräunlich, "
    "Robin Engler, "
    "Christian Ribeaud, "
    "François Martin",
    author_email="jaroslaw.surkont@unibas.ch, "
    "gerhard.braeunlich@id.ethz.ch, "
    "robin.engler@sib.swiss, "
    "christian.ribeaud@karakun.com, "
    "francois.martin@karakun.com",
    url="https://gitlab.com/biomedit/django-drf-utils",
    python_requires=">=3.7",
    install_requires=[
        "Django>=3.2",
        "djangorestframework>=3.12",
        "python-json-logger>=2",
    ],
    extras_require={
        "test": [
            "assertpy",
            "pytest",
            "pytest-django",
            "requests",
        ],
        "stubs": [
            "django-stubs",
            "djangorestframework-stubs",
            "types-requests",
        ],
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"django_drf_utils": ["py.typed"]},
    zip_safe=False,
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
)
