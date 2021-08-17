import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="add_one",
    version="0.0.1",
    author="Nishka Arora",
    author_email="naarora@caltech.edu",
    description="A small example package that adds one",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    # project_urls={
    #     "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={'console_scripts': ['add_one= add_one.__main__:main']},
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    package_data={
        "example_package_nishka24":["data/*.csv", "data/*.txt"]
    }
)