from setuptools import setup

setup(
    name='testit-allure-adaptor',
    version='0.1.7',
    description='Allure report adaptor for Test IT',
    long_description=open('README.rst').read(),
    url='https://pypi.org/project/testit-allure-adaptor/',
    author='Pavel Butuzov',
    author_email='pavel.butuzov@testit.software',
    license='Apache-2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    packages=['testit_allure_adaptor'],
    package_data={'testit_allure_adaptor': ['../connection_config.ini']},
    package_dir={'testit_allure_adaptor': 'src'},
    install_requires=['testit-pytest'],
    entry_points={'console_scripts': ['testit = testit_allure_adaptor.__main__:console_main']}
)
