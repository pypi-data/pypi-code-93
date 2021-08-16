import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bit-bee",
    version="1.0.1",
    author="fatelei",
    author_email="fatelei@gmail.com",
    description="bit-bee api client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fatelei/bit-bee",
    project_urls={
        "Bug Tracker": "https://github.com/fatelei/bit-bee/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    package_data={
        "": ["*.html"]
    },
    install_requires=[
        'requests'
    ]
)
