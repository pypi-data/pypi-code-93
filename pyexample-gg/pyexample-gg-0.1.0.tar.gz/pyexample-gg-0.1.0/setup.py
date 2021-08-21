from setuptools import setup

setup(
    name='pyexample-gg',
    version='0.1.0',    
    description='A example Python package',
    url='https://github.com/guyen800/pyexample',
    author='Guyen Gankhuyag',
    author_email='guyen800@gmail.com',
    license='BSD 2-clause',
    packages=['pyexample-gg'],
    install_requires=['numpy', 'pandas'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
