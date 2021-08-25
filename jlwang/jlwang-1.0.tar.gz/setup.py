from distutils.core import  setup
import setuptools
packages = ['jlwang']# 唯一的包名，自己取名
setup(name='jlwang',
	version='1.0',
	author='wjl',
    packages=packages, 
    package_dir={'requests': 'requests'},)
