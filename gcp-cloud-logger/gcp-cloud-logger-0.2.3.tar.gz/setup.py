import setuptools
from gcp_cloud_logger import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gcp-cloud-logger",  # Replace with your own username
    version=__version__,
    author="Sam Yao",
    author_email="turisesonia@gmail.com",
    description="Google Cloud Platform logging package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/turisesonia/gcp_cloud_logger",
    packages=setuptools.find_packages(exclude=["docs", "tests", "tests.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["google-cloud-logging", "ujson"],
    setup_requires=["wheel"],
)