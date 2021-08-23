import setuptools
long_desc = open("README.md").read()
required = ["setuptools>=42", "wheel", "beautifulsoup4"] # Comma seperated dependent libraries name
setuptools.setup(
    name="newsboat-subscribe",
    version="1.0.1", # eg:1.0.0
    author="Jonathan Li",
    license="MIT License",
    entry_points={
        'console_scripts': ['subscribe=package_src.main:main'],
    },
    description="Subscribe to youtube videos",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/jnbli/newsboat-subscribe",
    # project_urls is optional
    project_urls={
        "Bug Tracker": "https://github.com/jnbli/newsboat-subscribe/issues",
    },
    install_requires=required,
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)