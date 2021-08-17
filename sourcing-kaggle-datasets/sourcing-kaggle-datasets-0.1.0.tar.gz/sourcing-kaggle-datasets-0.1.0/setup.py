import pathlib
import setuptools

PACKAGE_NAME = "sourcing-kaggle-datasets"

VERSION = "0.1.0"

# The text of the README file
README = (pathlib.Path(__file__).parent / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(
    name=PACKAGE_NAME,
    license="MIT",
    version=VERSION,
    author="Bootcamp contributors",
    author_email="contributors@bootcamp-project.com",
    description="Data sourcing Kaggle Datasets Python",
    long_description=README,
    keywords="Python Package Boilerplate",
    long_description_content_type="text/markdown",
    url=f"https://gitlab.com/the-bootcamp-project/boilerplates/python-package",
    project_urls={
        'Documentation': f"https://sourcing.datasets.rtfm.page",
        'Repository': f"https://gitlab.com/the-bootcamp-project/boilerplates/python-package.git",
        'Bug Tracker': f"https://gitlab.com/the-bootcamp-project/boilerplates/python-package/-/issues",
        'Docker Hub': "https://hub.docker.com/r/tbcp/python",
        'Read More...': "https://bootcamp-project.com/",
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",

        # Indicate who your project is intended for
        "Topic :: Utilities",

        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",

        # Specify the Python versions you support here. In particular, ensure that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=setuptools.find_packages(
        where="lib", include=["bin", "tests"], exclude=["docs"]),
    package_dir={"": "lib"},
    include_package_data=True,
    python_requires=">=3.5"
)
