from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(

    name='deeperlearning',  # Required


    version='0.0.1',  # Required


    description='A python library for deep learning',  # Optional


    long_description=long_description,  # Optional


    long_description_content_type='text/markdown',  # Optional (see note above)


    url='https://github.com/riioze/DeeperLearning',  # Optional


    author='riioze',  # Optional


    author_email='riioze0@gmail.com',  # Optional


    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],


    keywords='development',  # Optional


    packages=find_packages(where='DeeperLearning'),  # Required

    python_requires='>=3.6, <4',


    install_requires=['numpy'],  # Optional



    entry_points={  # Optional
        'console_scripts': [
            'sample=sample:main',
        ],
    },


    project_urls={  # Optional
        'Source': 'https://github.com/riioze/DeeperLearning',
    },
)
