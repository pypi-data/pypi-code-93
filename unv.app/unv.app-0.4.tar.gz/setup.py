from setuptools import setup, find_packages

setup(
    name='unv.app',
    version='0.4',
    description="""Core app package with settings manipulation""",
    url='http://github.com/c137digital/unv_app',
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
    install_requires=[
        'cerberus',
        'unv.utils'
    ],
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
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'app = unv.app.bin:run'
        ]
    },
)
