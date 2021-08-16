from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='archiltest',
    version='0.0.3',
    description='Simple Addition',
    long_description=open('README.txt').read(),
    include_package_data=True,
    packages=['simple_test/myjar'],
    url='',
    author='Archil Chachanidze',
    author_email='archikochachanidze@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='calculator',
    install_requires=['']
)