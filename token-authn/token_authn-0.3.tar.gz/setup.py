from distutils.core import setup
setup(
  name = 'token_authn',         
  packages = ['token_authn'],   
  version = '0.3',      
  license='MIT',        
  description = 'Token Authentication',   
  author = 'Aravind R',                   
  author_email = 'aravind.gradient@gmail.com',     
  url = 'https://github.com/aravindalbert/authentication',   
  download_url = 'https://github.com/user/reponame/archive/v_02.tar.gz',    
  keywords = ['Authentication'],   
  install_requires=[           
          'fastapi',
          'boto3',
          'python-jose[cryptography]'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3.8',
  ],
)