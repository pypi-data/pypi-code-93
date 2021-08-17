# coding: utf-8
import setuptools

VERSION = "0.0.3"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nakalapycon",                     # This is the name of the package
    version=VERSION,                        # The initial release version
    author="Michael Nauge",        # Full name of the author
    url="https://gitlab.huma-num.fr/mshs-poitiers/plateforme/nakalapycon",
    project_urls={
        "Issues": "https://gitlab.huma-num.fr/mshs-poitiers/plateforme/nakalapycon/-/issues",
        "CI": "https://gitlab.huma-num.fr/mshs-poitiers/plateforme/nakalapycon/-/pipelines",
        "Changelog": "https://gitlab.huma-num.fr/mshs-poitiers/plateforme/nakalapycon/-/blob/master/CHANGELOG.md",
    },
    description="Librairie Python pour interagir avec Nakala (Nakala est un entrepôt de données de recherche en SHS développé par Huma-Num)",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["nakalapycon","NklTarget","constantes","nklPullCorpus"],             # Name of the modules inside the python package
    package_dir={'':'nakalapycon/src'},     # Directory of the source code of the package
    install_requires=['requests', 'pandas']           # Install other dependencies if any
)
