import setuptools

exec(open('src/scb_profile_x/version.py').read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scb_profile_x",
    version=__version__,
    author="Napat Paopongpaibul",
    author_email="napat.paopongpaibul@gmail.com",
    description="Module to generate profile X visualization using CSV or Pandas dataframe",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/snn2spade/scb_profile_x_package",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        'Pillow>=8.1.0',
    ],
)
