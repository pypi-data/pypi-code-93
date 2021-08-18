"""Setup for package."""
import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
VERSION = "2.1.3"

setup(
    name="webdi",
    version=VERSION,
    description=(
        "A library containing a simple dependency injection container that is optimized for web "
        "apps."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    author="Trey Cucco",
    author_email="fcucco@gmail.com",
    url="https://gitlab.com/tcucco/web-di",
    download_url="https://gitlab.com/tcucco/web-di/-/archive/master/web-di-master.tar.gz",
    package_data={"webdi": ["py.typed"]},
    packages=["webdi"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
    ],
    license="MIT",
    platforms="any",
    zip_safe=False,
)
