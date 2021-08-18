from setuptools import setup
from os import path

root = path.abspath(path.dirname(__file__))
with open(path.join(root, "readme.md"), "r") as readmefile:
    readme = readmefile.read()

setup(
    name="markdownmaker",
    version="0.4.0",
    description="An easy-to-use Python to Markdown generator.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/MoritzBrueckner/markdownmaker",
    author="Moritz Brückner",
    license="zlib",
    packages=["markdownmaker"],
    install_requires=[],
    python_requires=">=3.6",
    keywords="markdownmaker Markdown Syntax Layout Library Utility Generator Converter Tool",
    project_urls={
        "Documentation": "https://gitlab.com/MoritzBrueckner/markdownmaker",
        "Source": "https://gitlab.com/MoritzBrueckner/markdownmaker",
        "Tracker": "https://gitlab.com/MoritzBrueckner/markdownmaker/-/issues",
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: zlib/libpng License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Utilities",
        "Typing :: Typed"
    ],
)
