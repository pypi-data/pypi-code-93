"""
Packaging setup
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rulesengine",
    version="1.0.1",
    author="Thibaut Guirimand",
    author_email="tguirimand@gmx.fr",
    description="A rules engine to clarify your pipelines development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.guirimand.eu/tguirimand/rulesengine",
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Environment :: Plugins"
    ],
    packages=['rulesengine'],
    python_requires=">=3.6",
)
