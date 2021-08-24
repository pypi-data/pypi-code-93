from setuptools import setup
from os import path
import usrr16

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='usrr16',
    packages=[
        'usrr16',
    ],
    version=usrr16.__version__,
    license='gpl-3.0',
    description='USR-R16 / USR-R16-T controller',
    author='v1a0',
    author_email='contact@v1a0.dev',
    url="https://github.com/v1a0/usr-r16",
    download_url=f"https://github.com/V1A0/usr-r16/archive/refs/tags/v{usrr16.__version__}.tar.gz",
    keywords=['usr-r16', 'usr-r16-t', 'usrr16', 'usrr16t', 'lonhand', 'api'],
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.9',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
# https://pypi.org/classifiers/
