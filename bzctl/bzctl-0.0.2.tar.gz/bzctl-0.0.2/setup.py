#!/usr/bin/env python3
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='bzctl',  
     version='0.0.2',
     scripts=['bzctl'] ,
     author="Ahmet Yusuf Birinci",
     author_email="ayb84870@gmail.com",
     description="What that this script done is if you pass a run and the bunch of other arguments it collects the other arguments and putting the right arguments in right places on the yaml template.",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://bag.org.tr/proje/bulutzincir/bulut-zincir/blob/master/Scripts/bulut-zincir",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
     ],
 )