from setuptools import setup, find_packages


VERSION = '0.0.2'
DESCRIPTION = 'ParkingLot is a Python service imitating a parking lot like system.'
LONG_DESCRIPTION = 'The service indicates rather a vehicle allowed or not allowed to enter the parking lot.'

# Setting up
setup(
    name="parkinglot",
    version=VERSION,
    author="PsychoRover (Gil Chen)",
    author_email="<Gtorrent12@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['psycopg2', 'ocrspace'],
    keywords=['python', 'parking', 'lot', 'moon', 'parkinglot'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
