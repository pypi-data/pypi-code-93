from setuptools import *

setup(
    name = 'Python-Extension',
    version = '1.0.2',
    description = 'Python Extension Functions',
    license = 'GPL',
    author = 'Yile Wang',
    author_email = '36210280@qq.com',
    packages = find_packages(),
    python_requires = '>=2.7',
    include_package_data = True
    )

