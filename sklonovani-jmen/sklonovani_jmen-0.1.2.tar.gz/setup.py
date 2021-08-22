from distutils.core import setup
setup(
  name = 'sklonovani_jmen',
  packages = ['sklonovani_jmen'],
  version = '0.1.2',
  license='MIT',
  description = 'Module for using the API of www.sklonovani-jmen.cz in Python',
  author = 'Stanislav Kozák',
  author_email = 'kozakstanda23@gmail.com',
  url = 'https://github.com/standakozak/sklonovani_jmen',
  download_url = 'https://github.com/standakozak/sklonovani_jmen/archive/refs/tags/v_012.tar.gz',
  keywords = ['sklonovani-jmen', 'Czech grammar', 'API'],
  install_requires=[
          'requests'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8'
  ]
)
