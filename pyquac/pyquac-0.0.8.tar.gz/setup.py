from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='pyquac',
    version='0.0.8',
    description='Useful tools for quantum computing experiments, provided for BMSTU FMN',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent'
    ],
    author='Nikolay Zhitkov',
    author_email='nokolay.zh@gmail.com',
    keywords=['Two tone spectroscopy', 'plotly', 'pandas'],
    url='https://github.com/ikaryss/pyquac',
    download_url='https://pypi.org/project/pyquac/'
)

install_requires = [
    'pandas~=1.3.1',
    'numpy~=1.20.3',
    'ipython~=7.26.0',
    'ipywidgets~=7.6.3',
    'cufflinks~=0.17.3',
    'plotly~=4.14.3',
    'dash~=1.21.0 '
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
