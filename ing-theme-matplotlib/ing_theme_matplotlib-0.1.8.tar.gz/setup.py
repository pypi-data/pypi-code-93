import os
from os import path
import warnings

from setuptools import find_packages, setup
from setuptools.command.install import install

name = "ing_theme_matplotlib"
here = path.abspath(path.dirname(__file__))


#Set up the machinery to install custom fonts.  Subclass the setup tools install class in order to run custom commands during installation.  
class move_ttf(install):
    def run(self):
        """
        Performs the usual install process and then copies the INGMe fonts 
        that come with ing_theme_matplotlib into matplotlib's True Type font directory, 
        and deletes the matplotlib fontList.cache 
        """
        #Perform the usual install process
        install.run(self)
        #Try to install custom fonts
        try:
            import os, shutil
            import matplotlib as mpl
            import ing_theme_matplotlib as itm

            #Find where matplotlib stores its True Type fonts
            mpl_data_dir = os.path.dirname(mpl.matplotlib_fname())
            mpl_ttf_dir = os.path.join(mpl_data_dir, 'fonts', 'ttf')

            #Copy the font files to matplotlib's True Type font directory
            cp_ttf_dir = os.path.join(os.path.dirname(itm.__file__), 'fonts')
            for file_name in os.listdir(cp_ttf_dir):
                if file_name[-4:] == '.ttf':
                    old_path = os.path.join(cp_ttf_dir, file_name)
                    new_path = os.path.join(mpl_ttf_dir, file_name)
                    shutil.copyfile(old_path, new_path)
                    print ("Copying " + old_path + " -> " + new_path)

            #Try to delete matplotlib's fontList cache
            mpl_cache_dir = mpl.get_cachedir()
            mpl_cache_dir_ls = os.listdir(mpl_cache_dir)
            font_list_cache_names = ["fontList.cache", "fontList.py3k.cache"]
            for font_list_cache_name in font_list_cache_names:
                if font_list_cache_name in mpl_cache_dir_ls:
                    fontList_path = os.path.join(mpl_cache_dir, font_list_cache_name)
                    os.remove(fontList_path)
                    print("Deleted the matplotlib " + font_list_cache_name)
        except:
            warnings.warn("WARNING: An issue occured while installing the custom fonts for ing_theme_matplotlib.")

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    readme = f.read()

setup(
    name=name,
    version='0.1.8',
    description="ING styles for common plotting libraries",
    long_description=readme,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/ing_rpaa/ing_theme_matplotlib",
    author="Ahmet Emre Bayraktar - ING",
    author_email="aemrebayraktar@gmail.com",
    python_requires=">=3.5",
    packages=find_packages(),
    include_package_data=True,
    cmdclass={'install' : move_ttf},
    install_requires=[
        'matplotlib>=3.0.3',
        'jupyter>=1.0',
        'numpy>=1.14'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license="Apache 2.0",
)
