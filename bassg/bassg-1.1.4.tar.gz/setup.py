import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='bassg',
    version='1.1.4',
    license='MIT',
    author='Hunter Lawson',
    author_email='hawson7@gmail.com',
    description='BASSG - Basic Agile Static Site Generator',
    url='https://github.com/hunterlawson/bassg',
    project_urls={
        'Bug Tracker': 'https://github.com/hunterlawson/bassg/issues'
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords=['static site generator', 'bassg'],
    python_requires='>=3.6',
    py_modules=['bassg'],
    install_requires=['beautifulsoup4', 'click', 'markdown', 'Jinja2']
)