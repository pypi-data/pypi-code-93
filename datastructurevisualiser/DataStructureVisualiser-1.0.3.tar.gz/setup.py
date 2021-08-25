from setuptools import setup

with open("README.md", "r") as fh:
  long_description = fh.read()

setup(
  packages = ['DSViz'],   
  name = 'DataStructureVisualiser',       
  version = '1.0.3',      
  license='MIT',        
  description = 'DSViz is a simple and intuitive Python interface to multiple packages in order to help visualise different data structres while coding them. This package is developed mainly for students or developers who are in the process of learning data structures.',   # Give a short description about your library
  author = 'Ish Mehta',                   
  author_email = 'imehta34@gatech.edu',     
  url = 'https://github.com/IshMehta/DSViz',
  project_urls = {'GitHub' : 'https://github.com/IshMehta/DSViz',
                  'Documentation' : 'https://ishmehta.github.io/DSViz/'},     
  keywords = ['data structure', 'graph','list','array','tree','BST','AVL','binary','draw','visualise'],
  install_requires=[    
      'tk',
      'graphviz',
      'pillow'        
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Education',
    'Topic :: Education',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
  ],
  long_description=long_description,
  long_description_content_type="text/markdown",
  include_package_data = True,
)
