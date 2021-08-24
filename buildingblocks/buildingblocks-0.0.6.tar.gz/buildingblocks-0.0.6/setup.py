from setuptools import setup, find_packages
import os


# Setting up
setup(
    name="buildingblocks",
    version="0.0.6",
    author="Pavan Kumar Naraharisetti",
    author_email="<naraharisetti@gmail.com>",
    description="Some useful mathematical tools",
    long_description_content_type="text/markdown",
    long_description="Use the function *interpolate* to interpolate data. Xdata and Ydata are the first two arguments to the function *interpolate*. This (Xdata and Ydata) information is used to build a model and the third argument Xnew is the x-axis values of the interpolated data that the user wishes to have. The function returns Ynew for the given Xnew. The syntax is Ynew=interpolate(Xdata, Ydata, Xnew)",
    packages=find_packages(),
    install_requires=['numpy', 'pandas'],
    keywords=['python', 'interpolate', 'data analysis'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)