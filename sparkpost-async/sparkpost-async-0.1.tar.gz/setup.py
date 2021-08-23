import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

description = (
    'An asynchronous SparkPost email backend for Django.'
)

setuptools.setup(
    name='sparkpost-async',
    version='0.1',
    author='Armandt van Zyl',
    author_email='armandtvz@gmail.com',
    description=description,
    license='GPL-3.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/armandtvz/python-sparkpost-async',
    packages=setuptools.find_packages(exclude=['test_proj', 'test_project']),
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
    ],
    python_requires='>=3.8',
    install_requires=[
        'Django>=3.0',
        'sparkpost',
    ],
)
