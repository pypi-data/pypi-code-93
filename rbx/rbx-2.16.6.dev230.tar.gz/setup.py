# Copyright 2021 Rockabox Media Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import find_packages, setup

BOTO = 'boto3==1.17.55'

GOOGLE_DATASTORE = 'google-cloud-datastore>=2.1.0,<2.2'
GOOGLE_LOGGING = 'google-cloud-logging>=2.2.0,<2.3'
GOOGLE_PUBSUB = 'google-cloud-pubsub>=2,<2.5'
GOOGLE_STORAGE = 'google-cloud-storage>=1.36,<2'
GOOGLE_TASKS = 'google-cloud-tasks>=2.0,<3'

AUTH = [
    'google-cloud-firestore>=2.0.2,<2.1'
]
EDS = [
    GOOGLE_DATASTORE,
    'google-cloud-bigquery>=2.9.0,<2.10',
    'rfc3339',
]
MANIFEST = [
    BOTO,
    'opencv-python-headless==4.4.0.46'
]
MAPS = [
    'googlemaps>=4.4.2,<5',
]
MYSQL = [
    'PyMySQL',
    'sqlalchemy>=1.3,<1.4',
]
NOTIFICATIONS = [
    GOOGLE_PUBSUB,
]
QUEUES = [
    'redis==3.5.3',
    'hiredis==2.0.0',
    'rq==1.9.0',
    'rq-scheduler==0.11.0',
]


setup(
    name='rbx',
    version='2.16.6.dev230',
    license='Apache 2.0',
    description='Scoota Platform utilities',
    long_description='A collection of common tools for Scoota services.',
    url='http://scoota.com/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet',
    ],
    author='The Scoota Engineering Team',
    author_email='engineering@scoota.com',
    python_requires='>=3.7',
    install_requires=[
        'arrow>=1,<2',
        'Click<8',
        'colorama',
        'PyYAML>=5.4.1',
        'requests>=1.21.1',
    ],
    extras_require={
        # These are requirement bundles required for specific feature sets.
        'auth': AUTH,
        'buildtools': [
            'bumpversion==0.5.3',
            'check-manifest',
            'fabric~=2.5.0',
            'twine',
        ],
        'eds': MYSQL + EDS,
        'geo': MAPS,
        'manifest': MANIFEST,
        'mysql': MYSQL,
        'notifications': NOTIFICATIONS,
        'platform': AUTH + MANIFEST + MAPS + NOTIFICATIONS + QUEUES,
        'queues': QUEUES,

        # These are included for specific libraries. One can either add them directly to their
        # own project, or use one or more of these extras.
        # Their purpose is to show the supported versions of the libraries.
        'aws': [BOTO],
        'datastore': [GOOGLE_DATASTORE],
        'logging': [GOOGLE_LOGGING],
        'pubsub': [GOOGLE_PUBSUB],
        'storage': [GOOGLE_STORAGE],
        'tasks': [GOOGLE_TASKS],

        # Include them all for the test suite.
        'all': AUTH + EDS + MANIFEST + MAPS + MYSQL + NOTIFICATIONS + QUEUES + [
            GOOGLE_LOGGING,
            GOOGLE_STORAGE,
            GOOGLE_TASKS,
        ],
    },
    entry_points={
        'console_scripts': [
            'buildtools = rbx.buildtools.cli:program.run [buildtools]',
            'buildcreative = rbx.manifest.cli:build_creative [manifest]',
            'geocode = rbx.geo.cli:geocode [geo]',
            'reverse_geocode = rbx.geo.cli:reverse_geocode [geo]',
            'unpack = rbx.geo.cli:unpack [geo]',
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.md", "*.yaml"],
    }
)
