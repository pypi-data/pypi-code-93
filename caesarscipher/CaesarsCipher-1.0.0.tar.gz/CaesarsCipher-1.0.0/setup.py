from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name = "CaesarsCipher",
    author="Aaron Fritz",
    author_email="neversaydie2302@gmail.com",
    version = "1.0.0",
    description = "This is a simple python package for encrypting and decrypting text in Caesar’s Cipher.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    py_modules = ["CeasersCipher"],
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)   