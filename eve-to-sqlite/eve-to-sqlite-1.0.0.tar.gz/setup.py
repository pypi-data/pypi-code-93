from setuptools import setup
import os

VERSION = "1.0.0"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="eve-to-sqlite",
    description="Convert Eve measurement exports to a SQLite database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Jan-Erik Rediger",
    url="https://github.com/badboy/eve-to-sqlite",
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["eve_to_sqlite"],
    entry_points="""
        [console_scripts]
        eve-to-sqlite=eve_to_sqlite.cli:cli
    """,
    install_requires=["sqlite-utils>=2.7.2", "openpyxl"]
)
