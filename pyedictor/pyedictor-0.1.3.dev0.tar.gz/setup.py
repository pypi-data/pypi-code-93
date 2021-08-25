from setuptools import setup, find_packages


setup(
    name='pyedictor',
    version='0.1.3.dev0',
    license='Apache 2.0',
    description='fetch functionalities for EDICTOR',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    author='Johann-Mattis List',
    author_email='mattis_list@eva.mpg.de',
    url='',
    keywords='data',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points={"console_scripts": ["edictor=pyedictor.cli:main"]},
    zip_safe=False,
    platforms='any',
    python_requires='>=3.6',
    install_requires=[
        "lingpy", "lexibase", 
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'pytest>=4.3',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
)

