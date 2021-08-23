from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="annchor",
    version="1.0.0",
    author="Jonathan H",
    packages=["annchor"],
    description="Fast k-NN graph construction for slow metrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gchq/annchor",
    project_urls={
        "Bug Tracker": "https://github.com/gchq/annchor/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved",
    ],
    license="BSD",

    install_requires=[
        "joblib>=1.0.1",
        "numpy>=1.21.0",
        "numba>=0.53.1",
        "python-Levenshtein>=0.12.2",
        "pynndescent>=0.5.4",
        "scipy>=1.7.0",
        "scikit-learn>=0.0",
        "tqdm>=4.61.2",
    ],
    package_data={"annchor": ["data/*.npz", "data/*.gz"]},
)
