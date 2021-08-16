import setuptools
import pathlib
# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
VERSION = '0.1.4'

setuptools.setup(
    name="sympan",
    version=VERSION,
    author="Alem Memic",
    author_email="memicalem@gmail.com",
    description="Small Python library for downloading the data from AWS S3",
    long_description=README,
    long_description_content_type="text/markdown",
    url="http://www.github.com/~alem88/sympan/",
    download_url="https://github.com/alem88/sympan/archive/refs/tags/0.1.3.tar.gz",
    packages=setuptools.find_packages(exclude=("tests",)),

    zip_safe=False,
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "boto3==1.15.18",
        "joblib==1.0.1"
    ]
)
