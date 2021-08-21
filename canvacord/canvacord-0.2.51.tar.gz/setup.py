
   #name='canvacord',
   #version='0.2.51',
   #description='A Python Version of Canvacord',
   #license="MIT",
   #long_description=long_description,
   #author='blazen',
   #author_email='contact@fireballbot.com',
   #url="https://github.com/BlazenBoi/canvacord.py",
   #packages=['src/canvacord'],  #same as name
   #install_requires=["setuptools>=42", "wheel", "pillow", "discord", "asyncio", "aiohttp", "typing", "datetime"]

import setuptools

with open("README", "r") as fh:

    long_description = fh.read()

setuptools.setup(

    name="canvacord", # Replace with your username

    version="0.2.51",

    author="blazen",

    author_email="contact@fireballbot.com",

    description="A Python Version of Canvacord",

    long_description=long_description,

    long_description_content_type="text/markdown",

    url="https://github.com/BlazenBoi/canvacord.py",

    packages=setuptools.find_packages(),

    classifiers=[

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

        "Operating System :: OS Independent",

    ],

    python_requires='>=3.6',

)

#project_urls =
    #Bug Tracker = https://github.com/BlazenBoi/canvacord.py/issues
    #Discord Server = https://discord.com/invite/mPU3HybBs9
#classifiers =
    #Programming Language :: Python :: 3
    #License :: OSI Approved :: MIT License
    #Operating System :: OS Independent

#[options]
#package_dir =
    #= src
#packages = find:
#python_requires = >=3.6

#[options.packages.find]
#where = src