from setuptools import setup


setup(
    name='djtezos',
    version='0.5.0rc6',
    setup_requires='setupmeta',
    install_requires=[
        'django-model-utils',
        'cryptography',
        'djcall',
        'tenacity',
        'pytezos',
    ],
    extras_require=dict(
        test=[
            'django',
            'djangorestframework',
            'freezegun',
            'httpx',
            'pytest',
            'pytest-cov',
            'pytest-django',
            'pytest-asyncio',
        ],
    ),
    author='James Pic',
    author_email='jamespic@gmail.com',
    url='https://yourlabs.io/oss/cli2',
    include_package_data=True,
    license='MIT',
    keywords='cli',
    python_requires='>=3.8',
)
