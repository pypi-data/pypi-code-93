import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
     name='trex-lib',  
     version='0.2.21',
     author="Jack Lok",
     author_email="sglok77@gmail.com",
     description="TRex Core library package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://bitbucket.org/lokjac/trex-lib",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=[            
          'python-dateutil',
          'cryptography',
          'urllib3',
          'phonenumbers',
          'email_validator',
          'Flask-Caching',
          'Flask-Script',
          'basicauth',
      ],
 )

