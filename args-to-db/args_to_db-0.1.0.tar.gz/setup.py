import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

DESCRIPTION = "Runs python script in argument combinations and produces " + \
    "dataset of all results."

setup(
    author="schnellerhase",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Benchmark",
        "Topic :: System :: Distributed Computing",
        "Topic :: Utilities",
    ],
    description=DESCRIPTION,
    include_package_data=True,
    install_requires=['pandas', 'pytest'],
    keywords=["arguments", "pandas", "automatisation"],
    license="GPLv3",
    long_description_content_type="text/markdown",
    long_description=README,
    name="args_to_db",
    package_dir={"": "src"},
    packages=find_packages(where='src', exclude=[]),
    url="https://github.com/schnellerhase/args_to_db",
    # versioning: MAJOR.MINOR.TEST
    version="0.1.0",
)
