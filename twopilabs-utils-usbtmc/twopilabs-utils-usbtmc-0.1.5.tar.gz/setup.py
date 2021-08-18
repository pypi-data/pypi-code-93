import setuptools
import pathlib

DIR = pathlib.Path(__file__).parent
README = (DIR / 'README.md').read_text()

setuptools.setup(
    name='twopilabs-utils-usbtmc',
    version='0.1.5',
    author='2pi-Labs GmbH',
    author_email='info@2pi-labs.com',
    license='LGPLv3',
    description='Native generic USB Test and Measurement Class (USBTMC) implementation using PyUSB',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://2pi-labs.com',
    packages=setuptools.find_namespace_packages(),
    classifiers=[
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
    install_requires=[
        'pyusb',
        'libusb'
    ]

)
