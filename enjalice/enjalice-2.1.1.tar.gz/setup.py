from setuptools import setup

with open('README.md', encoding='utf-8') as f:
  long_description = f.read()

setup(
  name='enjalice',
  packages=['enjalice'],
  version='2.1.1',
  license='MIT',
  description='Async framework for Yandex Alice API',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Jotty',
  author_email='bard143games@gmail.com',
  url='https://github.com/jottyVlad/EnjAlice',
  download_url='https://github.com/jottyVlad/EnjAlice/archive/refs/tags/v2.1.1.tar.gz',
  keywords=['yandex', 'api', 'alice', 'яндекс', 'алиса', 'апи'],
  install_requires=[
          'pydantic'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      # Specify which python versions that you want to support
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
