import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="snek_dl",
    version="0.0.5",
    author="arta",
    author_email="disy455@gmail.com",
    description="An intuitive wrapper for youtube-dl",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/d-aughter/Snek",
    project_urls={
        "Bug Tracker": "https://github.com/d-aughter/Snek/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=["youtube-dl"],
    python_requires=">=3.6",
)
