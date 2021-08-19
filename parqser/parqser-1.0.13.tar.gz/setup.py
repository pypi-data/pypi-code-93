from setuptools import setup
import parqser


setup(
    name='parqser',
    version=parqser.__version__,
    description='Finally, a good parser',
    url='https://github.com/ARQtty/parqser',
    author='Ilya Shamov',
    author_email='ShamovIA@yandex.ru',
    license='MIT',
    packages=['parqser'],
    install_requires=['requests',
                      'lxml',
                      'loguru'],

    classifiers=[],
)
