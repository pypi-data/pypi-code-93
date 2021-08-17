from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='behave2cucumberZephyr',

    version='0.0.1',

    description='Behave to Cucumber json converter, modified to used with Zephyr',
    long_description='This project converts the behave json reports to a cucumber(like) json file, '
                     'that can be used with Zephyr Scale. The original work can be found here: '
                     'https://github.com/behalf-oss/behave2cucumber',

    url='https://github.com/KotieSmit/behave2cucumberZephyr',

    author='(original) Andrey Goldgamer, Zvika Messing, (adapted for Zephyr) Kotie Smit',
    author_email='',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.8',
    ],

    keywords='behave2cucumberZephyr setuptools development cucumber behave automation json Zephyr',

    packages=find_packages(),

    install_requires=[],

    extras_require={},

    data_files=[],

    py_modules=['__main__', '__init__'],
    
    entry_points={
        'console_scripts': [
            'behave2cucumberZephyr = behave2cucumberZephyr.behave2cucumberZephyr.__main__:main'
        ],
    },
)
