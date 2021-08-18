from setuptools import setup, find_packages
import os

setup_args=dict(
    name="PySCli",
    version="1.0",
    author="Sancho Godinho",
    description="A Module to Get User Terminal Commands...",
    long_description='Please See More Info on: https://github.com/sancho1952007/PySCli/',
    packages=['pyscli'],
    keywords=['cli()'],
    url="https://github.com/sancho1952007/PySCli/",
    license_files = ('LICENSE.txt'),
    project_urls={
        "Bug Tracker": "https://github.com/sancho1952007/PySCli/issues",
        }
    )
install_requires=[]

if __name__=='__main__':
    setup(**setup_args, install_requires=install_requires)
