from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.9'
DESCRIPTION = 'Quick data cleaning and preprocessing',   

# Setting up
setup(  
    name="Lazy_cleaner",
    version=VERSION,
    license='MIT', 
    author="Ahmed Ashraf Khalil",
    author_email="ahmedashraf13131@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    keywords=['python', 'Clean', 'Data', 'preprocessing', 'machine learning'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3',      
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'])