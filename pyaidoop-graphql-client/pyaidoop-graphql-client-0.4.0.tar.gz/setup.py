from setuptools import setup, find_packages

long_description = """A graphql communication library for AIdoop web-based application platform such as AIdoop-R.
The library includes graphql client api and defines graphql query and mutations for AIdoop-R
"""

INSTALL_REQUIRES = [
    "requests",
    "gql",
]

setup(
    name="pyaidoop-graphql-client",
    version="0.4.0",
    author="",
    author_email="",
    url="https://github.com/aidoop/vision-client-python.git",
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["LICENSE", "README.md", "requirements.txt"],
    },
    license="MIT",
    description="A graphql communication library for AIdoop web-based application platform",
    long_description=long_description,
    keywords=[
        "cooperative robot",
        "web-based application",
        "grpahql",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
