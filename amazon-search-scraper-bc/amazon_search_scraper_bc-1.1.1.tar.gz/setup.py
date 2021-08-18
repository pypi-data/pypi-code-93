from setuptools import setup, find_packages

LONG_DESCRIPTION = ""
with open('amazon_search_scraper_bc/README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

VERSION = '1.1.1'
DESCRIPTION = 'A package that fethes data from amazon.'

# Setting up
setup(
    name="amazon_search_scraper_bc",
    url = "https://github.com/barno1994/amazon_search_scraper_bc",
    version=VERSION,
    author="barno1994 (Barno Chakraborty)",
    author_email="<barno.baptu@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['bs4', 'beautifulsoup4','selenium', 'bottlenose', 'lxml', 'python-dateutil', 'six', 'soupsieve', 'urllib3', 'requests'],
    keywords=['amazon', 'scraper', 'amazonscraper', 'amazon search'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)