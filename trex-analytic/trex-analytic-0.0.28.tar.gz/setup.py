import setuptools
from pip._vendor.pkg_resources import require

setuptools.setup(
     name='trex-analytic',  
     version='0.0.28',
     author="Jack Lok",
     author_email="sglok77@gmail.com",
     description="TRex analytics package",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=[            
          'flask==1.1.2',
          'Jinja2',
          'requests',
          'google-oauth',
          'google-cloud-bigquery',
          'google-cloud-tasks',
          'flask-restful',
          'webargs',
      ]
 )



