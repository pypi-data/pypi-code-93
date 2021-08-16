import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="args_to_db",
    # versioning: MAJOR.MINOR.TEST
    version="0.0.5",
    description="Runs python script in specified argument combinations and produces a pandas dataframe of all results.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/schnellerhase/args_to_db",
    author="schnellerhase",
    keywords=["arguments", "pandas", "automatisation"],
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(where='src', exclude=[]),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=["pandas"],
)