from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pistachio",
    version="0.4.0",
    description="Pistachio aims to simplify reoccurring tasks when working with the file system.",
    py_modules=["pistachio"],
    package_dir={"": "src"},
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/mjakinowittering/pistachio",
    author="Matthew Akino-Wittering",
    author_email="matthew.akinowittering@gmail.com",
    install_requires = [],
    extras_require = {
        "dev": [
            "pytest >= 3.7",
            "flake8",
            "check-manifest",
            "schema",
            "twine",
        ],
    },
)
