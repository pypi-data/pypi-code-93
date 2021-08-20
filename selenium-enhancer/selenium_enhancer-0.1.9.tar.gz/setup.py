import setuptools


with open("README.md", "r") as fh:
    long_description  =  fh.read()

setuptools.setup(
    name = 'selenium_enhancer',  
    version = '0.1.9',
    scripts = ['selenium_enhancer.py'] ,
    author = "Danny Brown",
    author_email = "dannybrown37@gmail.com",
    description = "A package to enhance your Selenium WebDriver experience",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/dannybrown37/SeleniumEnhancer",
    packages = setuptools.find_packages(),
    package_data={'data' : ['Google-Analytics-Debugger_v2.8.crx.crx']},
    py_modules=['selenium_enhancer'],
    classifiers = [
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )