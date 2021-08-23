import setuptools

__version__ = "1.0.2"


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-talar",
    version=__version__,
    author="Talar",
    author_email="hello@talar.app",
    description="Django app for Talar",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://talar.app",
    packages=setuptools.find_packages(),
    install_requires=[
        'django >=2.1,<2.3', 'djangorestframework >=3.9,<4.0',
        'pyjwt >=1.7,<1.8',
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
