import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fdups",
    version="0.0.2",
    author="Ivaylo Ivanov",
    author_email="i.ivanov.2250@gmail.com",
    description="Finds all duplicate files in a list of files and folders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xloop10/fdups",
    license="MIT",
    py_modules=["fdups"],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Utilities"
    ],
)