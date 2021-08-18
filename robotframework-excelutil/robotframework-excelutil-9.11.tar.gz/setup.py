from setuptools import setup, find_packages

with open("README.txt", "r") as fh:
	long_description = fh.read()

setup(

    name='robotframework-excelutil',
    version='9.11',
    description='Robotframework library for excel xlsx file format',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/nagesh-bn/test1.git',
    author='Nagesh B Nagaraja Rao',
    author_email='nagesh.nagaraja@gmail.com',
    packages=find_packages(),
    install_requires=['openpyxl']
    
)
