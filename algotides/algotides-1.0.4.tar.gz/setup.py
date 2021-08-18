from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="algotides",
    version="1.0.4",
    description="GUI for Algorand algod and kmd deamon",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    project_urls={
        "GitHub": "https://github.com/CiottiGiorgio/algo-tides"
    },
    author="Giorgio Ciotti",
    author_email="gciotti.dev@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7, <4",
    install_requires=[
        "py-algorand-sdk>=1.4.1, <2.0.0",
        "jsonpickle>=2.0.0, <3.0.0",
        "PySide2>=5.0.0, <6.0.0",
        "qasync>=0.18.0, <1.0.0",
        "aioify>=0.4.0, <1.0.0"
    ],
    entry_points={
        "console_scripts": [
            "algotides = algotides.__main__:main"
        ]
    }
)
