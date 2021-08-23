import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="embodier",
    version="1.0.1",
    description="It generates the unique avatar, which save image into PNG, JPG, or Base64 string. you can use this package to give avatar to newly registered users on your application.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/2000prath/embodier",
    author="Prathamesh Patkar",
    author_email="2000prath@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["embodier"],
    include_package_data=True,
    install_requires=['numpy==1.19.5', 'Pillow==8.1.0'],
    entry_points={
        "console_scripts": [
            "embodier=embodier.__main__:AvatarGenerator",
        ]
    },
)