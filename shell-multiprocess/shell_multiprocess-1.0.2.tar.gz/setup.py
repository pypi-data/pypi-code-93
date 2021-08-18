import setuptools


with open("README.md", "r") as f:
    long_description = f.read()


setuptools.setup(
    name="shell_multiprocess",
    description="Simple shell script which runs lists of shell commands in parallel",
    version="1.0.2",
    author="Kris Urbanczyk",
    author_email="urbansanek@gmail.com",
    project_urls={
        "Source Code": "https://github.com/urbansan/futures_subproc",
    },
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["psutil", "dataclasses; python_version < '3.7'", "aiofiles"],
    entry_points={
        "console_scripts": [
            "multiprocess = shell_multiprocess.main:main",
        ]
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
)
