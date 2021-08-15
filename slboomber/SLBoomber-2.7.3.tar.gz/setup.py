import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SLBoomber",
    version="2.7.3",
    author="Shehan Lahiru",
    author_email="shehan6472@gmail.com",
    description="A small meassege bomber pkg ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shehan9909/boomber",
    project_urls={
        "Bug Tracker": "https://github.com/shehan9909/boomber",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
