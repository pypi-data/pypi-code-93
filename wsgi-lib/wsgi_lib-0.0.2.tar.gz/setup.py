import setuptools


setuptools.setup(
    name='wsgi_lib',
    version='0.0.2',
    description='WSGI Lib',
    author='Rustem Saitgareev',
    author_email='srustem3@yandex.ru',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where='src', include=['wsgi_lib', 'wsgi_lib.*']),
    python_requires='>=3.8',
    extras_require={
        'tests': [
            'pytest',
            'pytest-mock',
            'pytest-cov',
            'flake8',
            'mypy'
        ]
    }
)
