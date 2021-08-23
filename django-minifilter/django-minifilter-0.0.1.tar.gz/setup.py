import setuptools


with open('README.md', 'r') as readme:
    long_description = readme.read()


setuptools.setup(
    name='django-minifilter',
    version='0.0.1',
    author='dennisvang',
    author_email='djvg@protonmail.com',
    description='Minimal filter and search functionality for django list views.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django :: 3.2",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    url='https://github.com/dennisvang/django-minifilter',
    packages=['minifilter', 'minifilter.templatetags'],
    package_data={'minifilter': ['templates/*/*/*']},
    install_requires=['django==3.*'],
    python_requires='>=3.8',
)
