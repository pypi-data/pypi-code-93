import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LeagueLibrary",
    version="2021.08.15.4",
    author="Gabriel Veras",
    author_email="developergabrielveras@gmail.com",
    description="LeagueLibrary is a library for Python3 based on the origial Riot Games API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Groot-cmd/LeagueLibrary",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"":"LeagueLibrary"},
    packages=setuptools.find_packages(where="LeagueLibrary"),
    python_requires=">=3.9",
    install_requires=["requests==2.26.0"]
)
