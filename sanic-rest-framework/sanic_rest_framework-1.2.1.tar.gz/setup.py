from setuptools import find_packages, setup

setup(
    name='sanic_rest_framework',
    version='1.2.1',
    packages=find_packages(),
    description="Sanic rest api framework Similar to DRF ",
    author="WangLaoSi",
    author_email='hill@3io.cc',
    url="https://gitee.com/Wang_LaoSi/sanic_rest_framework",
    download_url='https://gitee.com/Wang_LaoSi/sanic_rest_framework/repository/archive/master.zip',
    install_requires=['sanic', 'tortoise-orm', 'ujson']
)

# python setup.py register sdist bdist_egg upload
