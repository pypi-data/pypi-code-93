from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

setup(
    name="Rottutils",
    version="0.1.1",
    description="Py library with useful utilities.",
    long_description=open("README.txt").read() + "\n\n" + open("CHANGELOG.txt").read(),
    url="https://github.com/Rotthin",
    author="Maciej 'Rotthin' Niziołek",
    author_email="rotthin_dev@protonmail.com",
    license="MIT",
    classifiers=classifiers,
    keyword="utils",
    packages=find_packages(),
    install_requires=['']
)