from setuptools import setup, find_packages
import parqser


setup(
    name='parqser',
    version=parqser.__version__,
    description='Finally, a good parser',
    url='https://github.com/ARQtty/parqser',
    author='Ilya Shamov',
    author_email='ShamovIA@yandex.ru',
    license='MIT',
    packages=find_packages(),
    install_requires=['requests',
                      'lxml',
                      'loguru'],

    classifiers=[],
)
