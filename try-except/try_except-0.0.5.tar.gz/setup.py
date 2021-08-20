import setuptools, os
from pathlib import Path
containing_dir = Path(__file__).parent

with open(containing_dir/"README.md", "r") as fhandle:
    long_description = fhandle.read()

setuptools.setup(
    name="try_except",
    version="0.0.5",
    author="NastyPigz",
    author_email="capitalismdiscordbot@gmail.com",
    description="Cheating Try Except",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NastyPigz/trycept",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
