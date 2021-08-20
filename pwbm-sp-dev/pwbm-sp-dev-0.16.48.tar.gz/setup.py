import setuptools
import os
import pathlib

EXCLUDE = ['luigi', 'selenium', 'boto3']


def copy_existing_requierements():
    requirements = []
    source_path = os.path.join(pathlib.Path(__file__).resolve(strict=True).parent.parent.parent.absolute(),
                               'requirements/scraper.txt')
    with open(source_path, 'r') as f:
        for row in f:
            if row.split('==')[0] not in EXCLUDE:
                requirements.append(row)
    return requirements


def get_requirements():
    try:
        copy_existing_requierements()
        with open('requirements.txt', 'w') as f:
            f.writelines(copy_existing_requierements())
    except FileNotFoundError:
        pass
    finally:
        with open('requirements.txt', 'r') as f:
            requirements = f.readlines()
    return [item.strip() for item in requirements]


def get_long_description():
    with open('README.md', 'r') as f:
        return f.read()


setuptools.setup(
    name='pwbm-sp-dev',
    version='v0.16.48',
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'pwbm-sp = sp_devtools:main',
        ]
    },
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)
