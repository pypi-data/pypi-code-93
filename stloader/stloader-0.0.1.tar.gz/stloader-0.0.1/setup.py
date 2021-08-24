import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='stloader',
    version='0.0.1',
    python_requires='>=3.5',
    entry_points={
        "console_scripts": ['stloader = stloader:cli']
        },
    author='BuildXYZ',
    author_email='buildxyz@gmail.com',
    description='Application to load custom and factory firmware on the STLINK-V3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/buildxyz-git/stloader',
    include_package_data=True,

    packages=setuptools.find_packages(),

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Embedded Systems'
     ],
 )
