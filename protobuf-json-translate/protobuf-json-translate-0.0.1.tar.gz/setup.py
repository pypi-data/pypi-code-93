from setuptools import setup

setup(
    name='protobuf-json-translate',
    version='0.0.1',
    description='A python package that support proto data conversion from json to proto(binary) and vice versa',
    url='https://github.com/samcaspus/protobuf-json-translator',
    author='samcaspus',
    author_email='sandeepguptan1998@gmail.com',
    license='MIT lisence',
    packages=['pjt'],
    install_requires=['setuptools',
                      'protobuf',
                      ],

    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
