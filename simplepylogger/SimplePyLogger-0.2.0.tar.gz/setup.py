from setuptools import setup

version = "0.2.0"

with open("README.md", "r") as fh:

    long_description = fh.read()

if __name__ == "__main__":
    setup(
        name="SimplePyLogger",
        version=version,
        description="Simple Python logger.",
        author="Lucas Meira",
        author_email="lima07.lucas@gmail.com",
        url="https://github.com/lucas-meira/Logger",
        project_urls={
            "Source": "https://github.com/lucas-meira/PyLogger",
        },
        long_description=long_description,
        long_description_content_type='text/markdown',
        packages=["PyLogger"],
        classifiers=[
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Software Development",
        ],
        python_requires=">=3.6",
        install_requires=[
            "colorama",
        ],
    )
