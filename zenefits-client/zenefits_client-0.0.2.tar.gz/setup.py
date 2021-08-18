from distutils.core import setup

setup(
  name = 'zenefits_client',
  packages = ['zenefits_client'],
  version = '0.0.2',
  license='MIT',
  description = 'Python wrapper for Zenefits API',
  long_description="See GitHub",
  long_description_content_type="text/markdown",
  author = 'Alex Lazich',
  author_email = 'lazich.alexander@gmail.com',
  url = 'https://github.com/alazich/zenefits-client',
  download_url = 'https://github.com/alazich/zenefits-client/archive/refs/tags/v0.0.2.tar.gz',
  keywords = ['api', 'hr', 'zenefits'],
  install_requires=[
          'validators',
          'beautifulsoup4',
          'requests'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
  ],
)