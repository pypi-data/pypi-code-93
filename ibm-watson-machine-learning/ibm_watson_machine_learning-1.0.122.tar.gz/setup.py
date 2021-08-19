# (C) Copyright IBM Corp. 2020.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
import os

with open('VERSION', 'r') as f_ver:
    VERSION = f_ver.read()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ibm_watson_machine_learning',
    version=VERSION,
    python_requires='>=3.7',
    author='IBM',
    author_email='svagaral@in.ibm.com, kaganesa@in.ibm.com, vbmithun@in.ibm.com, amadeusz.masny1@ibm.com',
    description='IBM Watson Machine Learning API Client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='BSD',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Natural Language :: English',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: POSIX :: Linux',
                 'Operating System :: Microsoft :: Windows',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Information Technology',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Internet'],
    keywords=["watson", "machine learning", "IBM", "Bluemix", "client", "API", "IBM Cloud"],
    url='http://ibm-wml-api-pyclient.mybluemix.net',
    packages=find_packages(),
    package_data={'': ['messages/messages_en.json']},
    install_requires=[
        'requests',
        'urllib3',
        'pandas<1.3.0,>=0.24.2',
        'certifi',
        'lomond',
        'tabulate',
        'packaging',
        'ibm-cos-sdk==2.7.*'
    ],
    include_package_data=True
)
