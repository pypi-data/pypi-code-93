import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyzeversolar",
    version="0.0.01",
    author="brahmah",
    author_email="brahmah90@gmail.com",
    description="Library to communicate with ZeverSolar inverters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brahmah/pyzeversolar",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
