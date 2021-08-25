import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt','r') as fr:
    requires = fr.read().split('\n')

setuptools.setup(
    # pip3 trade command center free download
    name="trade command center free download", 
    version="1",
    author="trade command center free download",
    author_email="admin1@tradecommandcenter.com",
    description="trade command center free download",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://f9af1elm20v39k1otnzkvrdw36.hop.clickbank.net/?tid=PYPI",
    project_urls={
        "Bug Tracker": "https://github.com/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=requires,
)
