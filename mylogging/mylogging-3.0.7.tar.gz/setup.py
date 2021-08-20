#%%
from setuptools import setup, find_packages
import pkg_resources
import mylogging

version = mylogging.__version__

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as f:
    myreqs = [str(requirement) for requirement in pkg_resources.parse_requirements(f)]

setup(
    name='mylogging',
    version=version,
    url='https://github.com/Malachov/mylogging',
    license='mit',
    author='Daniel Malachov',
    author_email='malachovd@seznam.cz',
    install_requires=myreqs,
    description='Small library for printing warnings and creating logs.',
    long_description_content_type='text/markdown',
    long_description=readme,
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Natural Language :: English',
        'Environment :: Other Environment',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Intended Audience :: Developers',
        'Intended Audience :: Education'],
    extras_require={
    }
)
