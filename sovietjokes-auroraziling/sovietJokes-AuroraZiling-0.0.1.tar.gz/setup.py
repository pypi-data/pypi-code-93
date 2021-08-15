import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sovietJokes-AuroraZiling",
    version="0.0.1",
    author="Mccree Lee",
    author_email="2935876049@qq.com",
    description="A library of Soviet jokes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AuroraZiling/Soviet-Jokes-Package",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
