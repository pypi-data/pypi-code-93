from setuptools import setup, find_packages
with open("README.md", "r") as fh:
  long_description = fh.read()

setup(
    name="flask_kraken_wq",
    packages=find_packages(),
    version='0.0.3',
    description="flask sync run ",
    author="wei.fu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='mefuwei@163.com',
    url="https://github.com/kraken-cloud/kraken",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'redis',
    ],

)
