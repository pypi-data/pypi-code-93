import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='stloader',
    version='0.0.2',
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
    download_url='https://github.com/buildxyz-git/stloader/archive/refs/tags/v_01.tar.gz',
    include_package_data=True,

    packages=setuptools.find_packages(),
    install_requires=[
            'click',
            'Crypto',
            'mmap',
            'tempfile',
            'pathlib',
            'logging',
            'time',
            'usb'
        ],
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
