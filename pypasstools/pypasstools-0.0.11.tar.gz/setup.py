import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pypasstools",
    version="0.0.11",
    author="Ayaan Imran Saleem",
    author_email="miskiacuberayaan2509@gmail.com",
    description="Passtools is a package that allows you to use tools with which you can do all kinds of stuff with passwords",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ayaan-Imran/passtools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)