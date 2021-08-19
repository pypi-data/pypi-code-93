import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mathtools-uio",
    version="0.0.1",
    author="Cory Alexander Balaton",
    author_email="cory.balaton@gmail.com",
    description="A package to help me do math",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thelexxirose/mathtools",
    project_urls={
        "Bug Tracker": "https://github.com/thelexxirose/mathtools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)