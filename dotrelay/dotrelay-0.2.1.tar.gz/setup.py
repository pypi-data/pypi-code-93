from distutils.core import setup
setup(
  name = 'dotrelay', # How you named your package folder (MyLib)
  packages = ['dotrelay'], # Chose the same as "name"
  version = '0.2.1', # Start with a small number and increase it with every change you make
  license= 'MIT', # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'a Python library starter template', # Give a short description about your library
  author = 'Jason Yung',
  author_email = 'json.yung@gmail.com',
  url = 'https://github.com/json2d/dotrelay', # Provide either the link to your github or to your website
  download_url = 'https://github.com/json2d/dotrelay/archive/v0.2.1.tar.gz',
  keywords = ['starter', 'template', 'python', 'thing'], # Keywords that define your package best
  install_requires= [],
  classifiers=[
    'Development Status :: 3 - Alpha', # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers', # Define your audience
    'Topic :: Utilities',
    'License :: OSI Approved :: MIT License', # Again, pick a license
    'Programming Language :: Python :: 3', # Specify which pyhton versions that you want to support
    # 'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)