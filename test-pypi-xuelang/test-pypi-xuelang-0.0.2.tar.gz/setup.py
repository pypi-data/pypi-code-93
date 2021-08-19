import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="test-pypi-xuelang",
    version="0.0.2",
    author="wunsch",
    author_email="wunsch0106@gmail.com",
    description="XuelangCloud vision algorithm labelci",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)