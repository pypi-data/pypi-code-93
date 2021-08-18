from setuptools import setup


setup(
    name             = "ssgrab",
    version          = "0.0.2",
    author           = "Brent Woodruff",
    author_email     = "brent@fprimex.com",
    url              = "http://github.com/fprimex/ssgrab",
    description="Get packages from SendSafely",
    long_description="Get packages from SendSafely",
    keywords="sendsafely",
    license          = "Apache",
    zip_safe         = False,
    py_modules       = [
                         "ssgrab"
                       ],
    classifiers      = [
                         "Development Status :: 4 - Beta",
                         "Intended Audience :: End Users/Desktop",
                         "License :: OSI Approved :: Apache Software License",
                         "Topic :: Utilities",
                       ],
    install_requires = [
                         "plac_ini",
                         "SendSafely-Python-API",
                       ],
    entry_points     = {
                         'console_scripts': [
                           'ssgrab  =  ssgrab:main',
                         ],
                       },
)
