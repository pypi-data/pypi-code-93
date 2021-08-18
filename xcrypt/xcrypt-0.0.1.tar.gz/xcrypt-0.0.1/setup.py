import setuptools

setuptools.setup(
    name="xcrypt",
    version="0.0.1",
    author="kgsensei",
    author_email="ceojeremy@rainydais.com",
    description="A Python encryption library.",
    long_description="XCrypt is a lightweight Python library for encrypting data.",
    long_description_content_type="text/markdown",
    url="https://github.com/kgsensei/XCrypt",
    project_urls={
        "Bug Tracker": "https://github.com/kgsensei/XCrypt/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)