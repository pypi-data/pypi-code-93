import os

from setuptools import find_packages
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="jsm_user_services",
    version="1.1.3",
    description="Middleware to intercept JWT auth token and more utils functions",
    long_description=README,
    long_description_content_type="text/markdown",
    include_package_data=True,
    author="Juntos Somos Mais",
    author_email="labs@juntossomosmais.com.br",
    license="MIT",
    url="https://github.com/juntossomosmais/jsm-user-service",
    packages=find_packages(),
    install_requires=["PyJWT==2.1.0", "requests"],
    extras_require={
        "drf": ["djangorestframework", "request-id-django-log"],
        "flask": ["flask", "flask-log-request-id"],
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django :: 2.1",
        "Environment :: Web Environment",
        "Natural Language :: Portuguese (Brazilian)",
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
