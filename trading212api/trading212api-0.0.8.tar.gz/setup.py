import setuptools

with open("README.md", "r") as fh: long_description = fh.read()

setuptools.setup(
    name="trading212api",
    version="0.0.8",
    author="Enrico Cambiaso",
    author_email="enrico.cambiaso@gmail.com",
    description="An unofficial API library for Trading212 based on Selenium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/auino/trading212api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
