from setuptools import setup

from os import path

def get_requirements(fn='requirements.txt', nogit=True):
   """Get requirements."""
   if path.exists(fn):
      with open(fn, 'r') as f:
        requirements = f.read().splitlines()
   else:
     requirements = []
   requirements = [r.split()[0].strip() for r in requirements if r and not r.startswith('#')]
   if nogit:
       requirements = [r for r in requirements if not r.startswith('git+')]
   return requirements
   
requirements = get_requirements()

print(f'Requirements: {requirements}')

extras = {
    'production': get_requirements('requirements_production.txt'),
    'AL': get_requirements('requirements_AL.txt'),
    'full': get_requirements('requirements_full.txt'),
    }
    
setup(
    # Meta
    author='Tony Hirst',
    author_email='tony.hirst@open.ac.uk',
    description='Python package installation for OU module TM351',
    name='ou-tm351-py',
    license='MIT',
    url='https://github.com/innovationOUtside/innovationOUtside/ou-tm351-py',
    version='0.0.5',
    packages=['ou_tm351_py'],

    # Dependencies
    install_requires=requirements,
    #setup_requires=[],
    extras_require=extras,

    # Packaging
    #entry_points="",
    include_package_data=True,
    zip_safe=False,

    # Classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Education',
        'License :: Free For Educational Use',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Visualization'
    ],
)


import subprocess
import sys

def install_external_requirements(fn="external_requirements.txt"):
   """Install additional requiremments eg including installs from github."""
   print(f"Installing external requirements from {fn}")
   #try:
   #   subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r", fn ])
   #except:
   #   print(f"Failed to install {fn}")

   requirements = get_requirements(fn, nogit=False)
   for r in requirements:
      try:
          print(subprocess.check_output([sys.executable, "-m", "pip", "install", "--no-cache-dir", r ]))
      except:
          print(f"Failed to install {r}")
   
install_external_requirements("external_requirements.txt")
