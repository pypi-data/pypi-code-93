import os
from setuptools import setup

BASE_DIR = os.path.dirname(__file__)


def read_requirements(filename: str):
    return open(os.path.join(BASE_DIR, "requirements", filename), "r").read().split("\n")


with open(os.path.join(BASE_DIR, 'README.md')) as readme:
    README = readme.read()

requirements = read_requirements("base_requirements.txt")
try:
    import rest_framework
except ImportError:
    requirements += read_requirements("rest_requirements.txt")

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-heaven',
    version='0.1.0',
    packages=['responses', 'services'],
    include_package_data=True,
    install_requires=requirements,
    license='MIT License',
    description='django-heaven brings structure and order to your django projects',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/knucklesuganda/django-heaven/',
    author='Andrey Ivanov',
    author_email='python.on.papyrus@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
