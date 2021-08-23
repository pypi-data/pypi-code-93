import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="benford_stats",
    version="0.0.5",
    author="Hannes Benne",
    author_email="hbenne@gmx.at",
    description="Statistical Test for Benfords Law",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/hbenne/benford/",
    project_urls={
        "Bug Tracker": "https://gitlab.com/hbenne/benford/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas","matplotlib"],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)