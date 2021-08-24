import os
from io import open

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

# https://packaging.python.org/guides/single-sourcing-package-version/
# http://blog.ionelmc.ro/2014/05/25/python-packaging/

PATH_ROOT = os.path.dirname(__file__)
builtins.__INTELLINO_SETUP__ = False

import intellino

def load_requirements(path_dir=PATH_ROOT, comment_char='#'):
    with open(os.path.join(path_dir, 'requirements.txt'), 'r') as file:
        lines = [ln.strip() for ln in file.readlines()]
    reqs = []
    for ln in lines:
        # filer all comments
        if comment_char in ln:
            ln = ln[:ln.index(comment_char)]
        if ln:  # if requirement is not empty
            reqs.append(ln)
    return reqs


# https://packaging.python.org/discussions/install-requires-vs-requirements /
# keep the meta-data here for simplicity in reading this file... it's not obvious
# what happens and to non-engineers they won't know to look in init ...
# the goal of the project is simplicity for researchers, don't want to add too much
# engineer specific practices

setup(
    name="intellino",
    version=intellino.__version__,
    license=intellino.__license__,
    description=intellino.__docs__,
    author=intellino.__author__,
    author_email=intellino.__author_email__,

    url = 'https://github.com/Intellino/intellino',
    download_url='https://github.com/Intellino/intellino',
    
    packages=find_packages(exclude=['tests']),

    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',    
    include_package_data=True,
    zip_safe=False,

    keywords=["intellino"],
    python_requires='>=3.6',
    setup_requires=[],
    install_requires=load_requirements(PATH_ROOT),

    classifiers=[
        'Natural Language :: English',

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Operating System :: OS Independent",
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Development Status :: 3 - Alpha'
    ],
    
)
