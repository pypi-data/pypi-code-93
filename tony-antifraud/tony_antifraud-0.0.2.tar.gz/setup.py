from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r",encoding='utf-8') as f:
  long_description = f.read()

setup(name='tony_antifraud',  # 包名
      version='0.0.2',  # 版本号
      description='A small example package',
      long_description=long_description,
      author='Tony',
      author_email='antifraudvip@163.com',
      url='https://pypi.org/manage/account/',
      install_requires=['xgboost'],
      license='BSD License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],
      )