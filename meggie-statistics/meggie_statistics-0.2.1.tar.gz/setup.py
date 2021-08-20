from setuptools import setup

setup(
    name='meggie_statistics',
    version='0.2.1',
    description='Statistics plugin for Meggie',
    license='BSD',
    packages=['meggie_statistics'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'meggie>=1.3.0'
    ]
)
