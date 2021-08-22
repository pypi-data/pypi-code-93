#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



### distutils is deprecated use setuptools instead
from setuptools import setup, find_packages, find_namespace_packages

import pathlib
import os
#import path



LICENSE_TYPE='Public Domain'
KEYWORDS='general, common, development, library'
REQUIRES=['numpy>=1,<2','boto3>=1,<2','Pillow>=8,<9','rsa>=3,<4','ruamel.yaml>=0,<1','opencv-contrib-python>=4,<5','pycairo>=1,<2','PyGObject>=3,<4']
URL='https://github.com/N-z0/CommonZ'

AUTHOR='N-z0',
AUTHOR_EMAIL='syslog@laposte.net'
MAINTAINER='N-z0',
MAINTAINER_EMAIL='syslog@laposte.net'

DOC_FILE='docs/description.md'
LICENSE_FILE='license.md'



SETUP = pathlib.Path(__file__).parent.resolve()
#os.system("echo here "+str(SETUP))

for name in os.listdir(SETUP) :
	if os.path.isdir(os.path.join(SETUP,name)) and not name in ("build","dist") and not name.endswith(".egg-info")  :
		DIRECTORY=name
		break
combo= DIRECTORY.split('-',1)
NAME=combo[0]
VERSION="1.0.0"#combo[1]
#print(DIRECTORY,compo,NAME,VERSION)

### Get the descriptions from description.md
with open(os.path.join(SETUP,"README.md"), encoding='utf-8') as f:
	description_lines=f.readlines()
	intro_index=description_lines.index("## 🚩 Intro\n")
	SHORT_DESCRIPTION=description_lines[intro_index+1].strip().strip("*")
	#os.system("echo "+str(short_description))
	description_index=description_lines.index("## ℹ️ Description\n")
	LONG_DESCRIPTION= "\n".join(description_lines[description_index+1:])

### get and make package list
packages=find_packages(where=os.path.join(DIRECTORY,'src'))
### find_namespace_packages is identical to find_packages except it would count a directory as a package even if it doesn’t contain __init__.py file
packages=find_namespace_packages(where=os.path.join(DIRECTORY,'src'))
#os.system("echo "+str(packages))
PACKAGES=[ '.'.join([NAME,pak]) for pak in packages ]
PACKAGES_DIRS={}
for pak in packages :
	PACKAGES_DIRS['.'.join([NAME,pak])]= os.path.join(DIRECTORY,'src',pak)



### Arguments marked as Required must be included for upload to PyPI.
### Fields marked as Optional may be commented out.
setup(
	### Required
	### The name of your project.
	### The first time you publish this package, this name will be registered for you.
	### It will determine how users can install this project,
	### e.g.: $ pip install sampleproject
	### And where it will live on PyPI: https://pypi.org/project/sampleproject/
	### there are some restrictions on what makes a valid project name
	### specification : https://packaging.python.org/specifications/core-metadata/#name
	### But this does not have to be the same as the folder name the package lives
	### in, although it may be confusing if it is not.
	### An example of where the package name and the directory do not match is Scikit-Learn: 
	### you install it using pip install scikit-learn, while you use it by importing from sklearn.
	name=NAME,

	### Required
	### The version of your package.
	### This is the version pip will report, 
	### and is used for when you publish your package on PyPI1.
	### Versions should comply with PEP 440: https://www.python.org/dev/peps/pep-0440/
	### also see : https://packaging.python.org/en/latest/single_source_version.html
	### version='X.Y.Z',
	version=VERSION,
	
	### With latest wheellooks like the license_file option has been deprecated.
	### use option "license_files =" instead.
	license_files=(os.path.join(DIRECTORY,LICENSE_FILE),),
	###also specify the license type
	license=LICENSE_TYPE,
	
	
	### Optional
	### This is a one-line description
	### or tagline of what your project does.
	### This corresponds to the "Summary" metadata field: https://packaging.python.org/specifications/core-metadata/#summary
	description=SHORT_DESCRIPTION,

	### Optional
	### This is a longer description of your project
	### that represents the body of text which users will see when they visit PyPI.
	### This field corresponds to the "Description" metadata field: https://packaging.python.org/specifications/core-metadata/#description-optional
	long_description=LONG_DESCRIPTION,
	
	### Optional
	### Denotes our long_description format
	### valid values are text/plain, text/x-rst, and text/markdown
	### Optional if long_description is written in reStructuredText (rst)
	### but required for plain-text or Markdown
	### if unspecified, "applications should attempt to render [the long_description] as text/x-rst; charset=UTF-8
	### and fall back to text/plain if it is not valid rst" (see link below)
	### This field corresponds to the "Description-Content-Type" metadata field
	### https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
	long_description_content_type='text/markdown',

	### Optional
	### used to assist searching.
	### This field adds keywords for your project which will appear on the project page.
	### keywords are separated by commas,
	### https://www.python.org/dev/peps/pep-0314/
	keywords=KEYWORDS,
	
	
	### Optional
	### This should be your name or the name of the organization which owns the project.
	author=AUTHOR,

	### Optional
	### This should be a valid email address corresponding to the author listed above.
	author_email=AUTHOR_EMAIL,

	### Optional
	### A string specifying the name of the current maintainer, 
	### (if different from the author)
	### Note that if the maintainer is provided, setuptools will use it as the author in PKG-INFO.
	maintainer=MAINTAINER,

	### Optional
	### A string specifying the email address of the current maintainer, if different from the author.
	maintainer_email=MAINTAINER_EMAIL,
	
	
	### Optional
	### This should be a valid link to the project's main homepage.
	### This field corresponds to the "Home-Page" metadata field:
	### https://packaging.python.org/specifications/core-metadata/#home-page-optional
	url=URL,

	### Optional
	### A string containing the URL from which this version of the package can be downloaded.
	### (This means that the URL can't be something like ".../package-latest.tgz",
	### but instead must be "../package-0.45.tgz".)
	download_url=URL+'/releases',

	### Optional
	### List additional relevant URLs about your project.
	### This is the place to link to bug trackers, source repositories, or where to support package development
	### https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
	#project_urls={
	#	'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
	#	'Funding': 'https://donate.pypi.org',
	#	'Say Thanks!': 'http://saythanks.io/to/example',
	#	'Source': 'https://github.com/pypa/sampleproject/',
	#	'Tracker': 'https://github.com/pypa/sampleproject/issues'
	#}
	
	
	### Required
	### A list of strings specifying the packages that setuptools will manipulate.
	### You can just specify package directories manually if your project is simple.
	### Or you can use find_packages() or find_namespace_packages()
	#packages=['momo.timer','momo.fs','momo.net'],
	packages=PACKAGES,
	
	### Alternatively,
	### A list of strings specifying the modules that setuptools will manipulate.
	### if you just want to distribute a single Python file, use the py_modules instead
	#py_modules=["my_module"],
	
	### Optional
	### A dictionary providing a mapping of package to directory names.
	### When your source code is in a subdirectory under the project root, e.g. `src/`,
	### it is necessary to specify the `package_dir` argument.
	#package_dir={'momo.timer': os.path.join(DIRECTORY,'src/timer'),'momo.fs': os.path.join(DIRECTORY,'src/fs'),'momo.net': os.path.join(DIRECTORY,'src/net')},
	package_dir=PACKAGES_DIRS,
	
	### A namespace package is a package that may be split and distributed across multiple package.
	### Each sub-package will be separately installed, used, and versioned.
	### Without, If many packages installed with same name, at module import only the one found first would be imported.
	### For example, zope package is a namespace package,
	### because subpackages like zope.interface and zope.publisher may be distributed separately.
	### pour linstant pas envie de devoir ecrire une doc pour chaque sous module, ni de leur atribuer des version
	#namespace_packages=['TopPackage'],
	
	
	### Required
	### Specify which Python versions you support. 
	### 'pip install' will check this and refuse to install the project if the version does not match.
	### See https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
	python_requires='>=3, <4',
	
	### A list of strings or comma-separated string.
	### Wheels do not use this field other than to include it in the metadata,
	### There is no further specification for the contents of this list
	### it is unstructured and free-form
	platforms=['GNU/Linux'],
	
	### Optional
	### This field lists other packages that your project depends on to run.
	### Any package you put here will be installed by pip when your project is installed,
	### so they must be valid existing projects.
	### For an analysis of "install_requires" vs pip's requirements files see:
	### https://packaging.python.org/en/latest/requirements.html
	install_requires=REQUIRES,
	
	### Optional
	### List of additional dependencies 
	### (optional features of your project) 
	### Users will be able to install these using the "extras" syntax,
	###for example:
	###   $ pip install sampleproject[dev]
	### Similar to `install_requires` above, these must be valid existing projects.
	### For example, a project might offer optional PDF output if ReportLab is installed,
	### These requirements will not be automatically installed
	#extras_require={
	#	'dev': ['check-manifest'],
	#	'test': ['coverage'],
	#},
	
	
	### Optional
	### If there are data files included in your packages that need to be installed, specify them here.
	### Suppose we have a schema.json in our project, which we place in exampleproject/data/schema.json.
	### If we want to include this in our package, we must use the package_data 
	### This will make sure the file is included in the package.
	### We can also choose to include all files based on a pattern
	### example: package_data={'sample': ['package_data.dat'],},
	#package_data=
	
	### providing the list of Python extensions to be built.
	### example:
	### 	ext_package='pkg'
	### 	ext_modules=[Extension('foo', ['foo.c']),Extension('subpkg.bar', ['bar.c'])]
	#ext_package=
	#ext_modules=
	
	### Optional
	### it is important to understand that entry points are a feature of the new Python eggs package format and are not a standard feature of Python.
	### To provide executable scripts, use entry points in preference to the "scripts" keyword.
	### Entry points provide cross-platform support and allow `pip` to create the appropriate form of executable for the target platform.
	### For example, the following would provide a command called `sample` which executes the function `main` from this package when invoked:
	#entry_points={
	#	'console_scripts': [
	#		'sample=sample:main',
	#	],
	#},
	
	### indicates this wheel has an extension module,
	### A subclass of Distribution to use.
	#distclass=
	
	
	### Optional
	### Classifiers help users find your project by categorizing it.
	### For a list of valid classifiers, see https://pypi.org/classifiers/
	classifiers=[
		### How mature is this project?
		'Development Status :: 5 - Production/Stable',
		
		### Indicate who your project is intended for
		'Intended Audience :: Developers',
		
		### Indicate what this package is about
		'Topic :: Software Development',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Libraries :: Application Frameworks',
		'Topic :: Software Development :: Libraries :: Python Modules',
		
		### Pick your license as you wish
		#'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
		'License :: Public Domain',
		
		### what operating systems are supported
		#'Operating System :: Android',
		#'Operating System :: Unix',
		#'Operating System :: POSIX :: GNU Hurd',
		'Operating System :: POSIX :: Linux',
		
		### Specify the Python versions you support.
		### In particular, ensure that you indicate you support Python 3.
		### These classifiers are *not* checked by 'pip install'.
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
		'Programming Language :: Python :: 3.10',
		'Programming Language :: Python :: 3 :: Only',
	]
)
