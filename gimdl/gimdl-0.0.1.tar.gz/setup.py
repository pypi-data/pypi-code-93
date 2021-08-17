from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gimdl',
    version='0.0.1',
    description='Google Image Search Downloader - using API ',
    py_modules=["gimdl"],
    package_dir={'': 'src'},
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],


    keywords='googleimages, images, search', 
    long_description=long_description,
    long_description_content_type="text/markdown"
)