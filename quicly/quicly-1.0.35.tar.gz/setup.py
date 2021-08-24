import os
import requests
import re
import sys
import json
import setuptools


root = os.path.dirname(os.path.abspath(__file__))


def load_pkg_info():
  info = dict()

  file = os.path.join(root, 'PKG-INFO')
  if os.path.isfile(file):
    with open(file, 'r+', encoding='utf-8') as fo:
      for line in fo.readlines():
        line = line.strip()
        kv = line.split(':', maxsplit=1)
        if len(kv) < 2:
          continue
        k = kv[0].strip().lower()
        v = kv[1].strip()

        info[k] = v

  return info


def getver(name, major=None, minor=None, patch=None):
  pattern = '{} {}'.format(name, '\\.'.join([f'({x})' if isinstance(x, int) else '(\\d+)' for x in (major, minor, patch)]))

  res = requests.get(f'https://pypi.org/project/{name}/')
  items = re.findall(pattern, res.content.decode())
  if not items:
    major = major if isinstance(major, int) else 0
    minor = minor if isinstance(minor, int) else 0
    patch = patch if isinstance(patch, int) else 0
  else:
    major, minor, patch = items[0]
    major = int(major)
    minor = int(minor)
    patch = int(patch)

  return major, minor, patch


def setup():
  is_sdist = False
  for arg in sys.argv:
    if arg == 'sdist':
      is_sdist = True
      break

  major = None
  minor = None
  patch = None

  if is_sdist:
    name = os.path.basename(root)
    ver_json_file = os.path.join(root, 'version.json')
    if os.path.isfile(ver_json_file):
      with open(ver_json_file, 'r+', encoding='utf-8') as fo:
        ver_json = json.loads(fo.read())  # type: dict
        major = ver_json.get('major', major)
        minor = ver_json.get('minor', minor)
        patch = ver_json.get('patch', patch)
    major, minor, patch = getver(name, major=major, minor=minor, patch=patch)
    version = f'{major}.{minor}.{patch+1}'
    url = f"https://gitee.com/muxiaofei/{name}"
  else:
    pkg_info = load_pkg_info()
    name = pkg_info['name']
    version = pkg_info['version']
    url = pkg_info['home-page']

  requirements = []

  requirements_txt = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
  if os.path.isfile(requirements_txt):
    with open(requirements_txt, 'r+') as fo:
      for line in fo.readlines():
        item = line.split('#')[0].strip()
        if len(item):
          requirements.append(item)

  setuptools.setup(
    name=name,
    version=version,
    keywords=[name],
    author="muxiaofei",
    author_email="muxiaofei@gmail.com",
    description="",
    long_description="",
    long_description_content_type="text/x-rst",
    url=url,
    packages=setuptools.find_packages(),
    classifiers=[
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
    ],
    install_requires=requirements,
  )


if __name__ == '__main__':
    setup()
