from setuptools import setup


setup(
    name="pyTRML",
    author="GrandMoff100",
    author_email="nlarsen23.student@gmail.com",
    version="0.0.0",
    packages=["trml"],
    install_requires=["colorama"],
    description="Terminal Rendering Markup Language",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown'
)
