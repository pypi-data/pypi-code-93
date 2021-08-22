"""
A collection of utility functions
"""
import setuptools

REQUIRED = [
    "beautifulsoup4",
    "numpy",
    "pandas",
    "scikit-learn",
    "spacy",
]

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name="five-one-one",
    version="1.4.3",
    author="ecowley",
    author_email="erik@stromsy.com",
    description="a collection of data science helper functions",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://datascience.stromsy.com",
    packages=[
        "five_one_one",
    ],
    ext_modules=[
        setuptools.Extension(
            "five_one_one.c",
            ["five_one_one/c/pyfib.c",],
        ),
    ],
    python_requires=">=3.7",
    install_requires=REQUIRED,
    classifiers=["Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
