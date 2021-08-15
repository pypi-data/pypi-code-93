from setuptools import setup, find_packages

setup(
    name="flask_kraken_wq",
    packages=find_packages(),
    version='0.0.1',
    description="flask sync run ",
    author="wei.fu",
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
