import setuptools

with open("./README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="checksum_calculator",
    version="1.0.0",
    author="SECRET Olivier",
    author_email="pypi-package-checksum_calculator@devo.live",
    description="Simple checksum calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/olive007/checksum-calculator",
    packages=["checksum_calculator"],
    package_data={
        "": ["*.txt"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        "Operating System :: OS Independent",
    ]
)
