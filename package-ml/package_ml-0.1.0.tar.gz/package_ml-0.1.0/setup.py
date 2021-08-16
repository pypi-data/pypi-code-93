from setuptools import setup
# https://anweshadas.in/how-to-upload-a-package-in-pypi-using-twine/

setup(
    name="package_ml",
    # Pour la version, utiliser incremental module
    version='0.1.0',
    description="Notre premier package de machine learning",
    author="Nouha, Adrien, Gwendélina",
    # url="https://github.com/anweshadas/gitcen",
    py_modules=['package_ml'],
    install_requires=[ 
        'Seaborn'
    ],
    # example:
    # entry_points='''
    #     [console_scripts]
    #     gitcen=gitcen:main
    # ''',

    entry_points='''
        [ml]
        package_ml=package_ml:ml
    ''',
    
    classifiers=(
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent'
    )
)