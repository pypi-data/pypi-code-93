import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jsonfilelogger",
    version="1.0.1",
    author="Manu De Buck",
    author_email="manu@mdebuck.org",
    description="A simple json file logger for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ManuDeBuck/python-json-filelogger",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires='>=3.6',
)