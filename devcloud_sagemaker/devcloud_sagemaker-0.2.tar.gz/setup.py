from setuptools import setup, find_packages

setup(
    name='devcloud_sagemaker',
    packages=find_packages(),
    version='0.2',
    description='Devcloud with Sagemaker',
    author='Jim',
    author_email='nowhere@test.com',
    url='https://github.com/DEV3L/python-package-archetype',
    download_url='https://github.com/DEV3L/python-package-archetype/tarball/0.4',
    keywords=['dev3l', 'archetype', 'pypi', 'package'],  # arbitrary keywords
    install_requires=[
        'pytest==2.9.2'
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    entry_points={
        'console_scripts': [
            'hello_world = devcloud_sagemaker.sm_client:print_hello_world'
        ]},
)
