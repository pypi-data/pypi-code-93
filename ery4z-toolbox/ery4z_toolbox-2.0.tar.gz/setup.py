from distutils.core import setup
setup(
  name = 'ery4z_toolbox',         # How you named your package folder (MyLib)
  packages = ['ery4z_toolbox'],   # Chose the same as "name"
  version = '2.0',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'My personal toolbox',   # Give a short description about your library
  author = 'Ery4z',                   # Type in your name
  author_email = 'prog.ery4z@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/Ery4z/ery4z-toolbox',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/Ery4z/ery4z-toolbox/archive/refs/tags/v2.tar.gz',    # I explain this later on
  install_requires=[            # I get to this in a second
          'pycryptodome',
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
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
)