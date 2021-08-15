import gitlab_client
import pathlib
from setuptools import setup, find_packages


# The directory containing this file
HERE = pathlib.Path(__file__).parent


# The text of the README file
README = (HERE / "README.md").read_text()


def load(filename):
    # use utf-8 if this throws up an error
    return open(filename, "rb").read().decode("utf-8")


setup(
    name="gitlab_v4",
    version="0.0.3",
    description="Wrapper for Gitlab API v4",
    long_description=README,
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
