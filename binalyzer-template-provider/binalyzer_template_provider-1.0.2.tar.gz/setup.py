import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

__tag__ = "v1.0.2"
__build__ = 112
__version__ = "{}".format(__tag__)

setuptools.setup(
    name="binalyzer_template_provider",
    version=__version__,
    author="Denis Vasilìk",
    author_email="contact@denisvasilik.com",
    url="https://binalyzer.denisvasilik.com",
    project_urls={
        "Bug Tracker": "https://github.com/denisvasilik/binalyzer/issues",
        "Documentation": "https://binalyzer.readthedocs.io/en/latest/",
        "Source Code": "https://github.com/denisvasilik/binalyzer/",
    },
    description="Binary Data Analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Operating System :: POSIX :: Linux",
    ],
    dependency_links=[],
    package_dir={"binalyzer_template_provider": "binalyzer_template_provider"},
    package_data={},
    data_files=[("", ["CHANGELOG.md"])],
    setup_requires=[],
    install_requires=[
        "antlr4-python3-runtime==4.8",
        "anytree>=2.8.0",
        "requests>=2.25.1"
    ],
    entry_points={},
)
