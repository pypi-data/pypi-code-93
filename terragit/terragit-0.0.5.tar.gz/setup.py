from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='terragit',
  version='0.0.5',
  description='terragit package',
  long_description=open('README.txt').read(),
  url='',  
  author='walid',
  author_email='walid.mansia@allence-tunisie.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='terragit',
  packages=find_packages(),
  install_requires=[''],
    entry_points = ({
          'console_scripts': [
              'terragit = terragit.__main__:main'
          ]
      })
)