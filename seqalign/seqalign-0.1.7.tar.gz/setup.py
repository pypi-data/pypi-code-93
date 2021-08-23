import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='seqalign',
    version='0.1.7',
    author='Anthony Aylward',
    author_email='anthony.aylward@protonmail.com',
    description='Manage sequence alignments',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/anthony-aylward/seqalign.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=['biopython', 'pyhg19', 'tempfifo', 'cutadapt'],
    entry_points={
        'console_scripts': [
            'seqalign=seqalign.doc:main',
            'seqalign-chip-seq=seqalign.chip_seq:main',
            'seqalign-atac-seq=seqalign.atac_seq:main'
        ]
    }
)
