from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = "Wrapper for Seaborn plotting methods"
LONG_DESCRIPTION = "Wrapper for Seaborn plotting methods that helps reduce redundant code to produce custom plots"

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="seabornWrapper", 
        version=VERSION,
        author="Michael Panicci",
        author_email="<mapanicci@gmail.com.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["seaborn","pandas","numpy","matplotlib"], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=["seaborn","plotting","wrapper"],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent"
        ]
)