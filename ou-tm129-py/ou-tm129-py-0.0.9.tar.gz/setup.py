from setuptools import setup

from os import path

def get_long_description():
    with open(
        path.join(path.dirname(path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()

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
    'AL': get_requirements('requirements_AL.txt')
    }




setup(
    # Meta
    author='Tony Hirst',
    author_email='tony.hirst@open.ac.uk',
    name='ou-tm129-py',
    url='https://github.com/innovationOUtside/ou-tm129-py',
    description='Python environment for TM129',
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    license='MIT License',
    packages=['ou_tm129_py'],
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
   #   print(f"Failed to install {fn}.")
   requirements = get_requirements(fn, nogit=False)
   for r in requirements:
      try:
          print(subprocess.check_output([sys.executable, "-m", "pip", "install", "--no-cache-dir", r ]))
      except:
        pass

install_external_requirements("external_requirements.txt")
