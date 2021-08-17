import pathlib
import json
import setuptools

# The text of the README file
README = (pathlib.Path(__file__).parent / "README.md").read_text()
VERSION = (pathlib.Path(__file__).parent / "VERSION").read_text().rstrip("\n")

tbcp = {}
with open('./.tbcp.json', "r") as tbcp_json:
    tbcp = json.load(tbcp_json)

# This call to setup() does all the work
setuptools.setup(
    name=tbcp["PACKAGE_NAME_PYPI"],
    license="MIT",
    version=VERSION,
    author=tbcp["PACKAGE_AUTHOR"],
    author_email=tbcp["PACKAGE_EMAIL"],
    description=tbcp["PROJECT_TITLE"],
    long_description=README,
    long_description_content_type="text/markdown",
    keywords=tbcp["PACKAGE_KEYWORDS"],
    url=tbcp["PROJECT_URL"],
    project_urls=tbcp["PROJECT_URLS"],
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
    packages=setuptools.find_packages(where="lib", include=["bin","tests"], exclude=["docs"]),
    package_dir={"": "lib"},
    include_package_data=True,
    python_requires=">=3.5"
)
