"""Setup for the agc (area under gain curves) package."""

import setuptools

with open('README.md', encoding='utf-8') as f:
    README = f.read()

setuptools.setup(
    author="François Théberge",
    author_email="theberge@ieee.org",
    name='agc',
    license="MIT",
    description='Python code to compute and plot (truncated, weighted) area under gain curves (agc)',
    version='v0.0.1',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/ftheberge/agc',
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    py_modules=["agc"],
    package_dir={'':'agc'},
    install_requires=['numpy'],
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Science/Research',
    ],
)
