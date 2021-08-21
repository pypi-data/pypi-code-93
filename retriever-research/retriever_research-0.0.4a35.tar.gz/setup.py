import setuptools
from pathlib import Path

with open("README.md", "r") as fh:
    long_description = fh.read()

version_file = Path(__file__).parent/"retriever_research"/"VERSION"
VERSION = version_file.open('r').read().strip()

setuptools.setup(
        name="retriever_research",
        version=VERSION,
        author="Armand McQueen",
        author_email="armandmcqueen@gmail.com",
        description="Fast, pure Python S3 downloader",
        long_description=long_description,
        long_description_content_type="text/markdown",
        # url="https://github.com/armandmcqueen/dataset",
        packages=setuptools.find_packages(),
        include_package_data=True,
        classifiers=[
            "Programming Language :: Python :: 3.7",
        ],
        install_requires=[
                'pykka',
                'boto3',
                'tqdm',
                'psutil',  # Profiler only
                'matplotlib',  # Profiler only
                'click',  # Log viewer
                'termcolor'  # Log viewer
        ],
        entry_points={
            'console_scripts': [
                'retlogger = retriever_research.log_viewer:main',
            ],
        },
)