from setuptools import setup, find_packages
import os


# Setting up
setup(
    name="buildingblocks",
    version="0.0.2",
    author="Pavan Kumar Naraharisetti",
    author_email="<naraharisetti@gmail.com>",
    description="Some useful mathematical tools",
    long_description_content_type="text/markdown",
    long_description="Some useful mathematical tools",
    packages=find_packages(),
    install_requires=['numpy', 'pandas'],
    keywords=['python', 'intrapolate' 'data analysis'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)