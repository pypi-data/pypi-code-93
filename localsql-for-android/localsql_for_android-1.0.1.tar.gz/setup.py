from distutils.core import setup
from setuptools import find_packages
 
setup(name = 'localsql_for_android',     # 包名
      version = '1.0.1',  # 版本号
      description = '',
      long_description = '', 
      author = '',
      author_email = '',
      url = '',
      license = '',
      install_requires = [],
      classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
      ],
      keywords = '',
      packages = find_packages('src'),  # 必填，就是包的代码主目录
      package_dir = {'':'src'},         # 必填
      include_package_data = True,
)
#!/usr/bin/env python
 