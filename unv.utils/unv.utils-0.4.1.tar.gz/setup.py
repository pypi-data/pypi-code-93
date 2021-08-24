from setuptools import setup, find_packages

setup(
    name='unv.utils',
    version='0.4.1',
    description="""Common helpers for unv framework""",
    url='http://github.com/c137digital/unv_utils',
    author='Morty Space',
    author_email='morty.space@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    extras_require={
        'dev': [
            'pylint',
            'pycodestyle',
            'pytest',
            'pytest-cov',
            'pytest-env',
            'pytest-pythonpath',
            'autopep8',
            'sphinx',
            'setuptools',
            'wheel',
            'twine'
        ]
    },
    zip_safe=True
)
