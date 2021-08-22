from setuptools import setup, Extension
setup(
  name = 'screenshotscloud',
  packages = ['screenshotscloud'],
  version = '1.0.4',
  description = 'ScreenshotsCloud Python screenshot generator',
  long_description_content_type = "text/markdown",
  long_description = open('./README.md', 'r').read(),
  author = 'Chris Hutchinson',
  author_email = 'chris@equalkit.com',
  license = 'MIT',
  url = 'https://screenshots.cloud/',
  keywords = ['screenshots', 'screenshots.cloud', 'firefox', 'browser'],
  classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)