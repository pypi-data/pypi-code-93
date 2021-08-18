import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask-errors-as-nested-dicts",
    version="0.0.1",
    author="Rafael A. Bizao",
    author_email="rabizao@gmail.com",
    description="Changes standard flask and jwt errors format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rabizao/flask-errors-as-nested-dicts",
    project_urls={
        "Bug Tracker": "https://github.com/rabizao/flask-errors-as-nested-dicts/issues",
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