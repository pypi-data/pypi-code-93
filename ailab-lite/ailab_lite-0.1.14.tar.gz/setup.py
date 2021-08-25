from __future__ import print_function
from setuptools import setup, find_packages
import os
from os.path import join as pjoin
from distutils import log

from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
    get_version,
)


here = os.path.dirname(os.path.abspath(__file__))

log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])

name = 'ailab_lite'

# Get ailab_lite version
version = get_version(pjoin(name, '_version.py'))

js_dir = pjoin(here, 'js')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(js_dir, 'dist', 'index.js'),
]

data_files_spec = [
    ('share/jupyter/nbextensions/ailab-lite', 'ailab_lite/nbextension', '*.*'),
    ('share/jupyter/labextensions/ailab-lite', 'ailab_lite/labextension', "**"),
    ("share/jupyter/labextensions/ailab-lite", '.', "install.json"),
    ('etc/jupyter/nbconfig/notebook.d', '.', 'ailab-lite.json'),
]

cmdclass = create_cmdclass('jsdeps', data_files_spec=data_files_spec)
cmdclass['jsdeps'] = combine_commands(
    install_npm(js_dir, npm=['yarn'], build_cmd='build:prod'), ensure_targets(jstargets),
)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup_args = dict(
    name=name,
    version=version,
    description='Jupyter Notebook extension GUI node editor',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'widgetsnbextension',
        'ipywidgets>=7.6.0',
        'fathom-lib',
    ],
    packages=find_packages(),
    zip_safe=False,
    cmdclass=cmdclass,
    author='Michal Zagalski',
    author_email='michal.zagalski@logicai.io',
    url='https://github.com/fathoms-io/ailab-lite',
    keywords=[
        'ipython',
        'jupyter',
        'widgets',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)

setup(**setup_args)
