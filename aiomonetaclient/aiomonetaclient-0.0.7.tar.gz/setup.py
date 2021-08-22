import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aiomonetaclient",
    version="0.0.7",
    author="Artem Ziborov",
    author_email="artimydin@gmail.com",
    description="Aio cleint for moneta merchant api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Thaumaturge/aiomonetaclient",
    project_urls={
        "Bug Tracker": "https://github.com/Thaumaturge/aiomonetaclient/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8.2",
    install_requires=[
        "aiohttp==3.7.4",
        "simplejson"
    ]
)