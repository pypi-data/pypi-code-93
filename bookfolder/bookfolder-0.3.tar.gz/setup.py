from os import path
from setuptools import setup, find_packages

current_directory = path.abspath(path.dirname(__file__))
with open(path.join(current_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="bookfolder",
    version="0.3",
    author="Anni Järvenpää",
    description="Convert an image into a bookfolding pattern",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/aajarven/bookfolder",
    packages=find_packages(),
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        "click",
        "imageio",
        "fpdf2",
    ],
    entry_points={
        "console_scripts": [
            "bookfolder-cli = bookfolder.scripts.cli:cli",
            "bookfolder = bookfolder.scripts.gui:start",
        ],
    },
)
