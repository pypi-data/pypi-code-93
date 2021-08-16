from setuptools import setup

setup(
   name='google_trans_new_tmp',
   version='1.2.2',
   description='A useful module',
   author='Man Foo',
   author_email='foomail@foo.com',
   packages=['google_trans_new'],  #same as name
   install_requires=['requests', 'six'], #external packages as dependencies
)