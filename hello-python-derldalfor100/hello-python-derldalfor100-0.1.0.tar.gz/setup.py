# modules you need
from setuptools import setup, find_packages

# The setup function is where you specify your project's attributes
setup(
    # package name
    name='hello-python-derldalfor100',
    # package version
    version='0.1.0',
    # short description
    description='A script that prints "hello python"',
    # the documentation displayed on pypi
    long_description=open('README.rst').read(),
    # not strictly necessary, but it's a good practice to provide a url if you have one (and you should)
    url='https://github.com/derldalfor100/hello-python-package',
    # you.  you want attribution, don't you?
    author='derldalfor100',
    # your email.  Or, *an* email.  If you supply an 'author', pypi requires you supply an email.
    author_email='derldalfor100@gmail.com',
    # a license
    license='Apache License 2.0',
    # "classifiers", for reasons.  Below is adapted from the official docs at https://packaging.python.org/en/latest/distributing.html#classifiers
    classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 4 - Beta',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',

            # Pick your license as you wish (should match "license" above)
             'License :: OSI Approved :: Apache Software License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.9',
    ],
    # keywords.  because classifiers are for serious metadata only?
    keywords="hello python insanely useful",
    # what packages are included.  'find_packages' will automatically find your packages, but you can list them manually ('hello_python') if you want.
    packages=find_packages(),
    # minimum requirements for installation (third-party packages your package uses)
    install_requires=[],
    # give your package an executable.
    entry_points={
        'console_scripts': [
            # <name>=<package>:<function>
            # when the user calls 'hello_python' on the cli, 'hello_python/__init__.py::_cli()" will be called.
            'hello_python=hello_python:_cli',
        ],
    }
)