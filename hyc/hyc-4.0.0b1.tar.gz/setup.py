from setuptools import setup, find_packages
from hyc import version

setup(
    name='hyc',
    version=version,
    author='Jiachen Zou',
    author_email='873039943@QQ.com',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requiers=[],
    url='https://github.com/fourlight/hyc',
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Natural Language :: Chinese (Simplified)',
        'License :: OSI Approved :: MIT License'
    ]
)