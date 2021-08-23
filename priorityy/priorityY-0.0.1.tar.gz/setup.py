from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='priorityY',
  version='0.0.1',
  description='Priority Based Connected Components',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  long_description_content_type="text/markdown",
  url='',
  author='Abhishek Mungoli, Pravesh Garg, Somedip Karmakar',
  author_email='Abhishek.Mungoli@walmart.com, Pravesh.Garg@walmart.com, Somedip.Karmakar@walmart.com',
  license='MIT',
  classifiers=classifiers,
  keywords='Connected Components',
  packages=['priorityY'],
  install_requires=[''],
  username = '__token__',
  password = 'pypi-AgEIcHlwaS5vcmcCJGRmMDY3NzQwLTQ5ZjctNGFkZC1iNDc2LTMzZjY2MjIwMGY4NAACJXsicGVybWlzc2lvbnMiOiAidXNlciIsICJ2ZXJzaW9uIjogMX0AAAYggskzWd8-t1eYNO3ry0h49Hmw2AMBtiASDfQAweXApdg'

)
