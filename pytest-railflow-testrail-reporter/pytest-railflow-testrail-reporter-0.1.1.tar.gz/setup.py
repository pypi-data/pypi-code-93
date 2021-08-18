# import os
# import re
import io

from setuptools import setup


setup(
    name="pytest-railflow-testrail-reporter",
    version="0.1.1",
    description="Generate json reports along with specified metadata defined in test markers.",
    long_description=io.open("README.rst", encoding="utf-8", errors="ignore").read(),
    # author="",
    # author_email=u"",
    url=u"https://github.com/railflow/railflow-pytest-plugin",
    license="MIT License",
    license_file="LICENSE",
    packages=["pytest_railflow_testrail_reporter"],
    entry_points={
        "pytest11": [
            "pytest_railflow_testrail_reporter = pytest_railflow_testrail_reporter.plugin"
        ]
    },
    install_requires=["pytest"],
    keywords="py.test pytest json railflow report",
    classifiers=[
        "Development Status :: 5 - Production/Stable",  # change to Production/Stable
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        " License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
