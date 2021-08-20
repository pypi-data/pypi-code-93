import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="m2lk",
    version='0.0.2',
    author="Vladimir Gratinskii",
    author_email="vovangrat@gmail.com",
    description="WotLK M2 files parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vladimir007/m2lk",
    project_urls={
        "Bug Tracker": "https://github.com/Vladimir007/m2lk/issues",
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
