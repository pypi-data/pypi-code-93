# coding: utf-8
from setuptools import setup
import os


README = os.path.join(os.path.dirname(__file__), 'README.md')

setup(name='moneyfmt',
      version='1.0.2',
      description='Converte tipo Decimal para uma string formatda como dinheiro.',
      long_description=open(README).read(),
      long_description_content_type="text/markdown",
      author="Jonatan Rodrigues", author_email="jonatanjrss@gmail.com",
      license="Copyright © 2001-2021 Python Software Foundation. All rights reserved.",
      py_modules=['moneyfmt'],
      zip_safe=True,
      platforms='any',
      include_package_data=True,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Framework :: Django',
          'Framework :: Flask',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: Portuguese',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries',
      ],
      url='http://gitlab.com/jonatanjrss/moneyfmt/',)
