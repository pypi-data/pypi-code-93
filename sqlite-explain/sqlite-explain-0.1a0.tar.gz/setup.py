from setuptools import setup
import os

VERSION = "0.1a0"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="sqlite-explain",
    description="Derive information about a SQLite query using EXPLAIN",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/sqlite-explain",
    project_urls={
        "Issues": "https://github.com/simonw/sqlite-explain/issues",
        "CI": "https://github.com/simonw/sqlite-explain/actions",
        "Changelog": "https://github.com/simonw/sqlite-explain/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["sqlite_explain"],
    install_requires=[],
    extras_require={"test": ["pytest"]},
    tests_require=["sqlite-explain[test]"],
    python_requires=">=3.6",
)
