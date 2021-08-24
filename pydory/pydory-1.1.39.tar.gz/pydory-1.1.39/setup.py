from setuptools import setup, Extension
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

#os.environ["CC"] = "gcc-10.2"
os.environ['CFLAGS'] = '-O3 -fopenmp -pthread -D SAVEPD'
setup(name="pydory",
      version="1.1.39",
      python_requires='>=3',
      description="Python interface for Dory",
      author="Manu Aggarwal",
      author_email="manu.aggarwal@nih.gov",
      ext_modules=[Extension("pydory", ["dorymodule.c"],headers=['sort.h'\
          ,'sort2.h','sort3.h','sort4.h','sort5.h','sort6.h'\
          ,'sort8.h','sort9.h', 'sort10.h'\
          ])],
      )
