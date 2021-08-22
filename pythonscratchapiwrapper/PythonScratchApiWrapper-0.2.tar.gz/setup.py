from distutils.core import setup
setup(
  name = 'PythonScratchApiWrapper',         # How you named your package folder (MyLib)
  packages = ['PythonScratchApiWrapper'],   # Chose the same as "name"
  version = '0.2',      
  license='MIT',        
  description = 'A python api wrapper for scratch',   
  author = 'Carter Pfaff',                   
  author_email = 'carterpfaff@gmail.com',      
  url = 'https://github.com/MelonMars/PSAW',   
  download_url = 'https://github.com/MelonMars/PSAW/archive/refs/tags/V_01.tar.gz',    
  keywords = ['Python', 'API Wrapper', 'API', 'scratch', 'Scratch'],   
  install_requires=[          
          'requests',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.9',
  ],
)
