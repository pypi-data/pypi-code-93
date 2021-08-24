from setuptools import setup, find_packages

VERSION = "0.0.4"
DESCRIPTION = "The LingoScript programming language"
LONG_DESCRIPTION = (
    "A programming language that allows you to write in different human languages"
)

# Setting up
setup(
    name="lingoshell",
    version=VERSION,
    author="Gav H",
    author_email="hi@lingoshell.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=["language"],
    classifiers=[
        "Intended Audience :: Developers",
    ],
    package_data={"": ["*.json"]},
)
