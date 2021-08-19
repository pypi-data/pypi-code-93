#!/usr/bin/python
import os
#from distutils.core import setup, Extension
from setuptools import setup, Extension
shmht = Extension('shmht',
    sources = ['shmht.c', 'hashtable.c'],
    extra_compile_args = '-g3 -Wall -Werror -O3 -march=native'.split(),
)

setup(
    name            = 'pyshmht3',
    version         = '0.1.3',
    author          = 'muyakongali',
    author_email    = 'muyakongali@gmail.com',
    description     = 'provide sharing memory based hash table for python',
    license         = "BSD",
    keywords        = "python extension sharing memory based hash table",
    url             = "http://github.com/felix021/pyshmht",
    ext_modules     = [shmht],
    packages        = ["pyshmht3"]
)
