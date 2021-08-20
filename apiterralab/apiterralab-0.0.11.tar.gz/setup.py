from setuptools import setup

INSTALL_REQUIRES = []
setup(
   name='apiterralab',
   version='0.0.11',
   description='breve descrição',
   author='TerraLab',
   author_email='terralab@gmail.com',
   packages=["apiterralab"],  #same as name
   install_requires= INSTALL_REQUIRES, #external packages as dependencies
)