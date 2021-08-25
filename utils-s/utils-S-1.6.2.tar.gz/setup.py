import setuptools
import utils

setuptools.setup(
    name='utils-S',
    version=utils.version,
    author="Sal Faris",
    description="Utility functions",
    packages=setuptools.find_packages(),
    Install_requires=[
        'requests'
    ],
    license='MIT',
    author_email='salmanfaris2005@hotmail.com',
    url='https://github.com/The-Sal/utils/',
    download_url='https://github.com/The-Sal/utils/archive/refs/tags/v1.6.2.tar.gz'
)
