from distutils.core import  setup
import setuptools
packages = ['wangpug']# 唯一的包名
setup(name='wangpug',
	version='1.0',
	author='wjl',
    packages=packages, 
    package_dir={'requests': 'requests'},)
