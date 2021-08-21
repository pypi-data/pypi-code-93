import setuptools

setuptools.setup(
    name="mlapiwrapper",
    version="0.0.1",
    author="Minh Le",
    author_email="author@example.com",
    description="A small example package",
    long_description="long_description",
    long_description_content_type="text/markdown",
    url="",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "./"},
    packages=setuptools.find_packages(where="./"),
)