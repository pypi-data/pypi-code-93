import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rrLovesbb",
    version="0.0.1",
    author="tzrj",
    author_email="tzrj@zeroday.com",
    description="rr",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://hack.md",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
