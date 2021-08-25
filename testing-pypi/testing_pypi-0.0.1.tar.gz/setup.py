from distutils.core import setup

setup(name='testing_pypi',
      packages = ['testing_pypi'],
      version='0.0.1',
      description='Just testing stuff',
      url='https://github.com/cbonafin/testing_pypi',
      download_url = 'https://github.com/cbonafin/testing_pypi/archive/refs/tags/0.0.1.tar.gz', #FILL IN LATER
      author='cbonafin',
      author_email='anabonafin@gmail.com',
      keywords = ['keyowrd1', 'keyword2', 'keyword3'],
      license='MIT', #YOUR LICENSE HERE!

      install_requires=['poetry'],  #YOUR DEPENDENCIES HERE
  

      classifiers=[
        'Development Status :: 3 - Alpha',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        'Intended Audience :: Developers',      
        'Programming Language :: Python :: 3.7',
        ],
)
