import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='Centre.PyCS',  
     version='0.2.0.1',
     author="BK",
     author_email="basknappers@gmail.com",
     download_url = 'https://github.com/akaitrade/Centre.PyCS/archive/refs/tags/0.1.0-Beta.tar.gz', 
     description="Credits Blockchain Implementation in Python",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/akaitrade/Centre.PyCS",
     packages=[
              'pycs',
              'pycs.api',
              'pycs.apidiag',
              'pycs.general',
          ],
    install_requires=[
          'ed25519',
          'thrift',
          'base58',
          'base58check',
      ],
    package_dir={'pycs': 'pycs'},
     entry_points={
        'console_scripts': ['my-command=pycs.Connector:main']
    },
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )