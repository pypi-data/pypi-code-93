import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jinjaMarkdown",
    version="0.0.7",
    author="Anthony Lazar",
    author_email="alazar@uwaterloo.ca",
    description="A package containing a markdown filter for jinja2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AnthonyGithubCorner/jinjaMarkdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
