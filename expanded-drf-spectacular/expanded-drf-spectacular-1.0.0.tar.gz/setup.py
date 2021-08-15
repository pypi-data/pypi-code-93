from setuptools import setup, find_packages


setup(
    name='expanded-drf-spectacular',
    version='1.0.0',
    description='This library helps to create endpoints schema with OpenAPI V.3 with difference in request and response serializers.',
    author='Amin Payamfar',
    packages=find_packages(),
    install_requires=['Django>=2.2', 'djangorestframework>=3.10', 'uritemplate>=2.0.0', 'PyYAML>=5.1', 'jsonschema>=2.6.0', 'inflection>=0.3.1']
)
