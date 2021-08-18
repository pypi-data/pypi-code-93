import pathlib
import json
import setuptools

README = (pathlib.Path(__file__).parent / "README.md").read_text()
VERSION = (pathlib.Path(__file__).parent / "VERSION").read_text().rstrip("\n")

tbcp = {}
with open('./.tbcp.json', "r") as tbcp_json:
    tbcp = json.load(tbcp_json)

setuptools.setup(
    name=tbcp["PACKAGE_NAME_PYPI"],
    license="MIT",
    version=VERSION,
    description=tbcp["PROJECT_TITLE"],
    author=tbcp["REPOSITORY_AUTHOR"],
    author_email=tbcp["REPOSITORY_AUTHOR_EMAIL"],
    keywords=tbcp["PACKAGE_KEYWORDS"],
    long_description=README,
    long_description_content_type="text/markdown",
    url=tbcp["PROJECT_URL"],
    project_urls=tbcp["PROJECT_URLS"],
    classifiers=tbcp["PROJECT_CLASSIFIERS"],
    packages=setuptools.find_packages(where="lib", include=["bin","tests"], exclude=["docs"]),
    package_dir={"": "lib"},
    include_package_data=True,
    python_requires=">=3.5"
)
