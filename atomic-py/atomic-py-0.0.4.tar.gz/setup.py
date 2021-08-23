from setuptools import setup

setup(
    name='atomic-py',
    version='0.0.4',
    packages=['atomic', 'atomic.channels'],
    package_dir={'atomic': 'atomic'},
    url='https://atomicarchitecture.hotaka.io',
    license='GPL',
    author='Sergio.Bermudez',
    author_email='sergio@hotaka.io',
    description='Atomic Architecture Framework',
    extras_require={},
    install_requires=['pika'])
