from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'A very basic example of calling your python app from terminal'
LONG_DESCRIPTION = 'A very basic example of calling your python app from terminal'

# Setting up
setup(
        name="evil_insult", 
        version=VERSION,
        author="Pranav Bhatia",
        author_email="<prav10194@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        include_package_data=True,
        install_requires=['requests'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)