import setuptools

setuptools.setup(
   name='RaminDownloader',
   version='0.1.0',
   author='Ramin Salahshoor',
   author_email='cr201512@fhstp.ac.at',
   url='https://github.com/raminsalah/RaminAparatDownloader.git',
   license='LICENSE.txt',
   description='By this package videos from aparat.com can be downloaded',
   long_description_content_type='text/markdown',
   long_description=open('README.md').read(),
   # packages=setuptools.find_packages,
   install_requires=[
       "Django >= 3",
       "pytest",
       "requests",
       "BeautifulSoup4",

   ],
)