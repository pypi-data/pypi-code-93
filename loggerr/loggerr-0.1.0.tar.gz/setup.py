from setuptools import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="loggerr",
    version="0.1.0",
    author="fiverr",
    author_email="sre@fiverr.com",
    description="Zero configuration logger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fiverr/python-loggerr",
    license="MIT",
    packages=['loggerr'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)
