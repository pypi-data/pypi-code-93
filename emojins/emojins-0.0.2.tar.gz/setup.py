from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: MacOS :: MacOS X',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='emojins',
  version='0.0.2',
  description='this is a package that addes emoji to text.',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Ibuki Yoshida',
  author_email='ibuki042004@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='', 
  packages=find_packages(),
  install_requires=['textblob'] 
)
