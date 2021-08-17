import pathlib
import setuptools

README = (pathlib.Path(__file__).parent / "README.md").read_text()

setuptools.setup(
    name="scienceio",
    version="0.3.2",

    description="ScienceIO Python SDK",
    long_description=README,
    long_description_content_type="text/markdown",

    url="https://github.com/ScienceIO",
    author="scienceio",
    author_email="info@science.io",

    classifiers=[
        "Programming Language :: Python :: 3",
    ],

    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=[
        "requests==2.26.0",
        "configparser==5.0.2"
    ],

    extras_requires={
        'test': [
            "pytest==3.0.3",
            "vcrpy==1.10.3"
        ]
    }
)
