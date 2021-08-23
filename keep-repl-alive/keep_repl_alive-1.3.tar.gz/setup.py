from distutils.core import setup
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'description.md'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='keep_repl_alive',
    packages=['keep_repl_alive'],
    version='1.3',
    license='MIT',
    description='A simple python module for keeping repls awake',
    author='Rishit',
    author_email='vermarishit039@gmail.com',
    url='https://github.com/IamEinstein/keep_alive',
    download_url='https://github.com/IamEinstein/keep_alive/archive/v_01.tar.gz',
    keywords=['replit', 'keep alive', 'flask', 'threading'],
    install_requires=[
        'flask',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
