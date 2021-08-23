import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

description = (
    'Allow a Django user to set a theme preference.'
)

setuptools.setup(
    name='django-theme',
    version='0.3',
    author='Armandt van Zyl',
    author_email='armandtvz@gmail.com',
    description=description,
    license='GPL-3.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/armandtvz/django-theme',
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
    ],
)
