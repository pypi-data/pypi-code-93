# setup.py
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="IntelliPy",
    version="0.9.19",
    author="Nicolas Ruffini",
    author_email="n.ruffini@gmx.de",
    description="Automatic IntelliCage data analysis using Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NiRuff/IntelliPy",
    packages=["intellipy"],
    install_requires=["numpy>=1.19.2", "pandas>=1.1.3", "xlsxwriter>=1.3.7"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
