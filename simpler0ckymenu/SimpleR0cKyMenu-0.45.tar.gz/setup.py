
from distutils.core import setup
setup(
  name = 'SimpleR0cKyMenu',         # How you named your package folder (MyLib)
  packages = ['SimpleR0cKyMenu'],   # Chose the same as "name"
  version = '0.45',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Creating Simple Menu for your program',   # Give a short description about your library
  author = 'R0cKy',                   # Type in your name
  author_email = 'konrad.soczi@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/R3GG3/menu',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/R3GG3/menu/archive/refs/tags/0.2.tar.gz',    # I explain this later on
  keywords = ['MENU', 'SIMPLE', 'PYTHON', 'R0cKy'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pynput',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
  ],
)