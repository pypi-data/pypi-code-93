from setuptools import setup

FASTANALIZER_VERSION = "0.1.3"

setup(
    name = 'fastanalizer',
    packages = ['fastanalizer', 'fastanalizer.pyfasta'],
    version = FASTANALIZER_VERSION,
    license='MIT',
    description="fastanalizer - Fast protein domain analysis tool",
    long_description="fastanalizer - Fast protein domain analysis tool",
    author = 'Alexandre Zanatta Vieira',
    author_email = 'al-zanatta@hotmail.com',
    url = 'https://github.com/alezanatta/fastanalizer',
    download_url = 'https://github.com/alezanatta/fastanalizer/archive/refs/tags/v0.1.3.tar.gz',    # I explain this later on
    keywords = ['BIOINFORMATICS', 'PROTEIN', 'PHYLOGENY'],
    entry_points={
        'console_scripts': [
            'fastanalizer = fastanalizer:main'
        ]
    },
    include_package_data=True,
    install_requires=[
            'plotly>=4.9,<5',
            'biopython>=1.78',
            'numpy>=1',
            'pandas>=1',
            'scikit-learn',
            'requests>=2.21',
            'kaleido'
        ],
    classifiers=[
    'Development Status :: 3 - Alpha',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    ],
)