from distutils.core import setup
from setuptools import find_packages

try:
    from Cython.Build import cythonize
except ImportError:
    print('Cython is required.')
    exit(1)

setup_info={
    'name':'cxzip',
    'version':'1.0.0',
    'description':'Drip-in replacement of zipfile._ZipDecrypter for python 3.7+',
    'url':'https://github.com/multiSnow/czipdecrypter',
    "author":"Cognexa Solutions s.r.o.",
    "author_email":"info@cognexa.com",
    'classifiers':[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: C',
        'Programming Language :: Cython',
    ],
    "include_package_data":True,
    "data_files":[
        (
            ".",
            [
                "czipdecrypter.pyx","cfunc.c","crctable.c","czipdecrypter.c",

            ]
        )
    ],

    'keywords': ['zipfile','zip','decryption'],
}

if __name__=='__main__':
    setup_info['ext_modules']=cythonize('czipdecrypter.pyx')
    setup(**setup_info)
