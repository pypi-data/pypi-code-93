from setuptools import setup, find_packages
import pathlib

PACKAGE_DIRECTORY = pathlib.Path(__file__).parent.resolve()

long_description = (PACKAGE_DIRECTORY / 'README.md').read_text(encoding='utf-8')

setup(
    name='dragons_fire',
    description='A test suite to provide simple testing of workflows',
    version='0.1.5',
    url='https://github.com/kilonzi/gragons',
    author='John Kitonyo',
    author_email='jkitonyo@broadinstitute.org',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='dragon, tests, tickets',
    packages=find_packages(where="./src", exclude=("./tests",)),
    python_requires='>=3.6, <4',
    install_requires=['selenium==3.141.0', 'chromedriver-autoinstaller'],
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'dragon=dragon:main',
        ],
    },
)
