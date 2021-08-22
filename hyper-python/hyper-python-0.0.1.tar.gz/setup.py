from setuptools import find_packages, setup

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='hyper-python',
    version='0.0.1',
    author='Hyper',
    author_email='support@hyper.co',
    description='Python library for the Hyper API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/meta-labs/hyper-python',
    project_urls={
        'Documentation': 'https://docs.hyper.co/reference',
        'Source Code': 'https://github.com/meta-labs/hyper-python',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.0',
)
