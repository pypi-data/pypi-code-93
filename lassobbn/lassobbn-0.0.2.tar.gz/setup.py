from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_desc = fh.read()

setup(
    name='lassobbn',
    version='0.0.2',
    author='Jee Vang',
    author_email='g@oneoffcoder.com',
    packages=find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests')),
    description='Learning Bayesian Belief Networks with LASSO',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    url='https://github.com/oneoffcoder/lassobbn',
    keywords=' '.join(['bayesian', 'belief', 'network', 'multivariate', 'conditional', 'gaussian',
                       'linear', 'causal', 'causality', 'structure', 'parameter', 'lasso']),
    install_requires=['numpy', 'scipy', 'networkx', 'pandas'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Development Status :: 5 - Production/Stable'
    ],
    include_package_data=True,
    test_suite='nose.collector'
)
