import setuptools


with open('README.md', mode='r', encoding='utf-8') as f:
    readme = f.read()


requirements = [
    'requests>=2.26.0',
]


setuptools.setup(
    name='tew652brp',
    version='0.0.4',
    author='fl0pp5',
    description='Interface for working with the TEW-652BRP router API ',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    project_urls={
        'Documentation': 'https://tew-652brp.readthedocs.io/',
        'Source': 'https://github.com/fl0pp5/TEW-652BRP',
    },
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
