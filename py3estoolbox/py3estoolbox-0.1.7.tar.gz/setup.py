import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name          = 'py3estoolbox',
    version       = '0.1.7',
    author        = 'Great Tomorrow',
    author_email  = 'gr82morozr@gmail.com',
    description   = 'A Python3 tools and utilities collection for Elasticsearch',
    licence       = 'MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    url           = 'https://github.com/gr82morozr/py3estoolbox.git',  
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],

    keywords    = 'toolbox',
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires = ['elasticsearch', 'requests']

)