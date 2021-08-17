from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    # Define library name, this is what is used along with `pip install`
    name="streamlit-azure-ad-login",


    # Define the author of the repository.
    author="Juan Huarte, Ramiro Gallo",


    # Define the version of this library.
    # Read this as
    #   - MAJOR VERSION 0
    #   - MINOR VERSION 1
    #   - MAINTENANCE VERSION 0
    version="0.1.1",
    

    # Here is a small description of the library. This appears
    # when someone searches for the library on https://pypi.org/search.
    description="Python package to use a login with Azure AD",


    # I have a long description but that will just be my README
    # file, note the variable up above where I read the file.
    long_description=long_description,

    # This will specify that the long description is MARKDOWN.
    long_description_content_type="text/markdown",
    
    # These are the dependencies the library needs in order to run.
    install_requires=[
        "streamlit>=0.85.1",
    ],

    # here are the packages I want "build."
    packages=find_packages(),


    include_package_data=True,


    # Here I can specify the python version necessary to run this library.
    python_requires=">=3.6",

    classifiers=[],
    
)
