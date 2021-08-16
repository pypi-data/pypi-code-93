from distutils.core import setup



setup(
  name = 'intelli-sms-gateway',         # How you named your package folder (MyLib)
  packages = ['intelli-sms-gateway'],   # Chose the same as "name"
  version = '0.0.2',      # Start with a small number and increase it with every change you make
  license = 'MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A package extending developable features of the Intelli-Africa Solutions SMS Gateway',   # Give a short description about your library
  author = 'Intelli Africa Solutions',                   # Type in your name
  author_email = 'info@intelliafrica.solutions',      # Type in your E-Mail
  keywords = ['SMS', 'Bulk Sms', 'Bulk Email'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'requests',
          'pandas'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    "License :: OSI Approved :: MIT License", # Again, pick a license
    'Programming Language :: Python :: 3.6',
  ],
)