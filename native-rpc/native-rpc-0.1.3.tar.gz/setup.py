import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="native-rpc",
    version='0.1.3',
    author="Howyoung Zhou",
    author_email="howyoungzhou@yahoo.com",
    description="Native RPC framework for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HowyoungZhou/native-rpc",
    packages=setuptools.find_packages(),
    install_requires=[
        'aiohttp',
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
