import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nbcommon",  # Replace with your own username
    version="0.1.53",
    author="chang@nextbillion.ai",
    author_email="chang@nextbillion.ai",
    description="nbcommon pkgs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'PyYAML>=5.1.2',
        'pydantic>=1.5',
        'aiohttp>=3.6.2',
        'osrmfb>=0.1.0',
        'prometheus-client>=0.7.1',
    ],
    python_requires='>=3.6',
    include_package_data=True,
)
