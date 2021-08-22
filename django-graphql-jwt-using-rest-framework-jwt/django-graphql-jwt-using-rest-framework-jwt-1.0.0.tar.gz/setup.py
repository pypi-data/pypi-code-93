import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="django-graphql-jwt-using-rest-framework-jwt",
    version="1.0.0",
    description="we use rest-framework-jwt algorithms to implement in django-graphql-jwt",
    long_description=README,
    long_description_content_type="text/markdown",
    # url="",
    author="hieucao192",
    author_email="hieucaohd@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["graphql_jwt"],
    include_package_data=True,
    install_requires=["djangorestframework-simplejwt", "Django", "PyJWT", "graphene_django"],
    # entry_points={
    #     "console_scripts": [
    #         "realpython=reader.__main__:main",
    #     ]
    # },
)