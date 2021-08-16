from setuptools import setup, find_packages

VERSION = '0.0.3'
DESCRIPTION = 'panther_analysis detections exposed in a convienent python module'


setup(
    name="panther_detections",
    version=VERSION,
    description=DESCRIPTION,
    packages=find_packages('./'),
    install_requires=[
        'policyuniverse',
        'requests',
        'jsonpath-ng'
    ]
    
)
