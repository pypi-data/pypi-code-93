import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="popcorngl",
    packages=['popcorngl'],
    version="2",
    author="Gpopcorn",
    author_email="",
    description="A module to render 3D graphics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gpopcorn/PopcornGL",
    project_urls={
        "Bug Tracker": "https://github.com/Gpopcorn/PopcornGL/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
    ],
    python_requires=">=3.6",
)
