import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="aviv-aws-costexplorer",
    version="0.1.2",
    description="Aviv AWS CostExplorer python library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aviv-group/aviv-aws-costexplorer",
    author="Jules Clement",
    author_email="jules.clement@aviv-group.com",
    packages=setuptools.find_packages(),
    install_requires=[
        "boto3>=1.17.43",
        "botocore>=1.20.43",
        "python-dateutil>=2.8.1"
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest>=6.2.2"],
    extras_require={
        "datastore": [
            "awswrangler>=2.6.0",
            "pandas>=1.2.3",
            "numpy>=1.20.2"
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Office/Business",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: System",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Typing :: Typed"
    ],
    use_2to3=False,
    zip_safe=False
)
