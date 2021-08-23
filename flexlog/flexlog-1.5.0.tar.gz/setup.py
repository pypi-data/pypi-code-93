import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flexlog", # Replace with your own username
    version="1.5.0",
    author="Sven Flake",
    author_email="sven.flake@optano.com",
    description="A convenience package to add a flexible logger easily.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/optano/flexlog",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)