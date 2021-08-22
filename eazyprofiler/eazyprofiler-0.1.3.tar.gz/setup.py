from setuptools import setup
import versioneer
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

requirements = [
    # package requirements go here
]

setup(
    name='eazyprofiler',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="EazyProfiler is forked version of Lazyprofiler which is a simple utility to collect CPU, GPU, RAM and GPU Memorystats while the program is running.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT",
    author="Damianos Park",
    author_email='damianospark@gmail.com',
    url='https://github.com/damianospark/eazyprofiler',
    packages=['eazyprofiler'],
    entry_points={
        'console_scripts': [
            'eazyprofiler=eazyprofiler.cli:cli'
        ]
    },
    install_requires=requirements,
    keywords='eazyprofiler',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
