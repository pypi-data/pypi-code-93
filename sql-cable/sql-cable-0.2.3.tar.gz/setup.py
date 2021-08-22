import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sql-cable",
    version="0.2.3",
    author="Logtism",
    author_email="nickhodder52@gmail.com",
    description="SQL-Cable is package designed to make it easier to work with a flask app and sqlite3 database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/logtism/sql-cable",
    project_urls={
        "Bug Tracker": "https://github.com/logtism/sql-cable/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
