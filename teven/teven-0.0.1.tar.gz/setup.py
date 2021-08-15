from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='teven',
  version='0.0.1',
  description='To retrieve even numbers between two numbeers',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Trimurthulu Chinni',
  author_email='trimuchinni23@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='even', 
  packages=find_packages(),
  install_requires=[''] 
)