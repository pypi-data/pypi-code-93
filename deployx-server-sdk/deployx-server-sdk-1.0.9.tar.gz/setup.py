import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deployx-server-sdk",
    version="1.0.9",
    author="CaptainKryuk",
    author_email="sir.kryukov@gmail.com",
    description="Programm for fast deploy and autotests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CaptainKryuk/deployx-server-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/CaptainKryuk/deployx-server-sdk/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        'urllib3'
    ],
    python_requires=">=3.6",
)