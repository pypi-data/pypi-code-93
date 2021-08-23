# from os import name
from setuptools import find_packages,setup
setup(
	name="kisaan-shopping",
	packages=find_packages(),
	install_requires=["pymongo[srv]","json","datetime"],
	version="0.1.2",
	description="This is kisaan_shopping_app utils",
	long_description="this too much long description",
	author="Aditya",
	author_email="mightybros98@outllok.com",
	url="https://www.kisaan.com.au/",
	download_url="https://www.w3school.com",
	keywords=["kisaan_shopping_app_utils","https://www.kisaan.com.au/","stable",
	"kisaan_shopping"],
	license="MIT",
	classifiers=[
    	'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    	'Intended Audience :: Developers',      # Define that your audience are developers
    	'Topic :: Software Development :: Build Tools',
    	'License :: OSI Approved :: MIT License',   # Again, pick a license
    	'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    	'Programming Language :: Python :: 3.4',
    	'Programming Language :: Python :: 3.5',
    	'Programming Language :: Python :: 3.6',
  ],	
)