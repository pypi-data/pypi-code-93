from setuptools import setup

install_requires = [
    'wagtail >=2.11',
]

factories_requires = [
    'factory-boy >=3.1,<3.2',
    'wagtail-factories >=2.0.1',
]

test_requires = factories_requires + [
    'pytest',
    'pytest-django',
    'pytest-cov',
    # code quality
    'black',
    'flake8 >=3.5',
    'flake8-black',
    'flake8-isort',
    'isort >=5.0',
]

setup(
    install_requires=install_requires,
    extras_require={
        'factories': factories_requires,
        'test': test_requires,
    },
)
