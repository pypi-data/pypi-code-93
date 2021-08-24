import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bbcloud-python-sdk",
    version="0.0.18",
    author="BBCloud",
    author_email="zealiemai@gmail.com",
    description="bbcloud python sdk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bbcloudGroup/bbcloud_python_sdk",
    packages=setuptools.find_packages(),
    install_requires=[
        'oss2==2.14.0',
        'synology-api==0.1.3.3',
        'esdk-obs-python==3.21.4',
        'requests==2.25.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
# python3 setup.py sdist bdist_wheel && python3 -m twine upload --repository pypi dist/*
