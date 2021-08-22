from distutils.core import setup

setup(
  name = 'falcon-jwt-guard',
  packages = ['falcon_jwt_guard'],
  version = '0.0.3',
  license='MIT',
  description = 'Simple JWT Authentication and nothing else for Falcon REST API.',
  author = 'Jesse Pham',
  author_email = '10214230+Phamiliarize@users.noreply.github.com',
  url = 'https://github.com/Phamiliarize/falcon-jwt-guard',
  download_url = 'https://github.com/Phamiliarize/falcon-jwt-guard/archive/refs/tags/v0.0.3.tar.gz',
  keywords = ['falcon', 'rest', 'api', 'jwt', 'auth'],
  install_requires=[
          'falcon',
          'pyjwt',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)