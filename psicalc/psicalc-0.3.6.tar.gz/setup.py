import setuptools

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="psicalc",
    keywords=['bioinformatics'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    version="0.3.6",
    author="Thomas Townsley",
    author_email="thomas@mandosoft.dev",
    description="Algorithm for clustering protein multiple sequence alignments using normalized mutual information.",
    url="https://github.com/mandosoft/psi-calc",
    packages=setuptools.find_packages(),
    install_requires=['pandas', 'scikit-learn'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
