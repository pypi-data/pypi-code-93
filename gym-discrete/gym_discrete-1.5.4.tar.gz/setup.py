#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import setuptools
from pathlib import Path
#from setuptools import setup
setuptools.setup(name='gym_discrete',
      version='1.5.4',
      description="A OpenAI Gym Env for discrete",
      long_description=Path("README.md").read_text(),
      long_description_content_type="text/markdown",
                 author="Claudia Viaro",
                 license="MIT",
      packages=setuptools.find_packages(include="gym_discrete*"),
      install_requires=['gym']  # And any other dependencies needed
)

