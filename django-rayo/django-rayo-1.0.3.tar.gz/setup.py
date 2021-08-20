import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='django-rayo',
    version='1.0.3',
    packages=['rayo'],
    description='Django Rayo Integration',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Linets Development Team',
    author_email='dteam@linets.cl',
    url='https://gitlab.com/linets/ecommerce/oms/integrations/django-rayo/',
    license='MIT',
    python_requires=">=3.7",
    install_requires=[
        'Django>=3',
        'requests>=2.25.1'
    ]
)
