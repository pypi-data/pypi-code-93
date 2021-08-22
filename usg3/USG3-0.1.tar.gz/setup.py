from setuptools import setup, find_packages

VERSION = '0.1' 
DESCRIPTION = 'USG3 Data API'
LONG_DESCRIPTION = 'This project creates a python package that is able to fetch,process and visualize geospatial data from the usg3 amazon dataset'

# Setting up
setup(
        name="USG3", 
        version=VERSION,
        author="Blaise Papa",
        author_email="blaisepke@gmail.com",
        description=DESCRIPTION,
        
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], 
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 1 - Planning",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)