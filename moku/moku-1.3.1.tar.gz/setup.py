from setuptools import setup
import os.path

setup(
    name="moku",
    version="1.3.1",
    author='Liquid Instruments',
    author_email='info@liquidinstruments.com',
    packages=['moku'],
    package_dir={'moku': 'moku'},
    package_data={
        'moku': [
            os.path.join('instruments', '*'),
            os.path.join('examples', '*'),
            os.path.join('data', '*')]
    },
    entry_points={
        'console_scripts': [
            'moku=moku.cli:main',
        ]
    },
    license='MIT',
    long_description=("Python scripting interface to the "
                      "Liquid Instruments Moku"),

    url="https://github.com/liquidinstruments/pymoku",
    download_url=("https://github.com/liquidinstruments/"
                  "moku/archive/%s.tar.gz") % "1.3.1",

    keywords=['moku', 'mokugo', 'liquid instruments', 'test', 'measurement', 'lab',
              'equipment'],

    python_requires='>=3.5',

    install_requires=[
        'requests>=2.18.0',
        'zeroconf',
    ],

    zip_safe=False,  # Due to bitstream download
)
