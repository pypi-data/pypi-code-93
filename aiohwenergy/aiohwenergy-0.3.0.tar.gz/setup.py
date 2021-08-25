"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages


long_description = open("README.md").read()

setup(
    name="aiohwenergy",
    version="0.3.0",
    license="Apache License 2.0",
    url="https://github.com/DCSBL/aiohwenergy",
    author="DCSBL",
    author_email="github@ducosebel.nl",
    description="Python module to talk to HomeWizard Energy Devices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    zip_safe=True,
    install_requires=list(val.strip() for val in open("requirements.txt")),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
