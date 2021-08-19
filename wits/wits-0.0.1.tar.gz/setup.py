from setuptools import setup, find_packages

with open('README.md', 'r') as readme_file:
    readme = readme_file.read()

requirements = ['numpy', 'pandas']

setup(
    name='wits',
    version='0.0.1',
    author='Wits AI',
    author_email='eyalgl@gmail.com',
    description='Brain Computations in Python',
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords=[],
    url='https://github.com/wits-ai/wits/',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    # package_data={'datasets': ['wits/resources/*']},
    classifiers=[
        'Programming Language :: Python :: 3.9',
    ],
)
