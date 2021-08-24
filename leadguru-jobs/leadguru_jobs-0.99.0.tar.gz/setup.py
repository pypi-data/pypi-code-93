import json
from urllib import request
from pkg_resources import parse_version
from setuptools import setup

package_name = "leadguru_jobs"


def versions():
    url = f'https://pypi.python.org/pypi/{package_name}/json'
    releases = json.loads(request.urlopen(url).read())['releases']
    return sorted(releases, key=parse_version, reverse=True)


try:
    version_parts = versions()[0].split(".")
except:
    version_parts = "0.0.0".split(".")

version_parts[1] = f'{float(version_parts[1]) + 1}'
last_version = ".".join(version_parts[0:-1])

install_requires = [
      'loguru',
      'pydantic==1.8.1',
      'cachetools>=3.1.0'
]
with open("requirements.txt") as fs:
    install_requires = install_requires +\
                       [req for req in fs.readlines() if req.startswith("leadguru-")]

setup(name=package_name,
      version=f'{last_version}',
      description='LGT jobs builds',
      packages=['lgt_jobs', 'lgt_jobs.jobs', 'lgt_jobs.templates'],
      include_package_data=True,
      install_requires=install_requires,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'Environment :: Console',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Internet',
      ],
      author_email='developer@leadguru.co',
      zip_safe=False)
