import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="suanpan_custom_code",
    version="0.0.2",
    author="zcw607",
    author_email="zcw607@gmail.com",
    description="python package for suanpan custom code library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/Tony607",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ),
    entry_points={
        "console_scripts": [
            "run_code=suanpan_custom_code.custom_python_code:main"
        ]
    },
)
