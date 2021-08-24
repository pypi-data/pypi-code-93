"This script takes component urls as input and pushes data to snappyflow under plugin etl."

from setuptools import find_packages, setup
import io
import os
import re

def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())

dependencies = ['click','elasticsearch','schedule','requests','pycrypto',"PyYAML","urllib3"]


setup(
    name='sfapmetl',
    version='0.1.6',
    url='https://github.com/Veeresh-dot-Pattar/sf-apm-etl',
    license='BSD',
    author='Veeresh Pattar',
    author_email='veeresh.pattar@maplelabs.com',
    description='This script takes component urls as input and pushes data to snappyflow under plugin etl',
    long_description=read("README.md"),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'sf-apm-etl = sf_apm_etl.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

