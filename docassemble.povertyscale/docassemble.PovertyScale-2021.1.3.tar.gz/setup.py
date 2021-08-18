import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')
def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='docassemble.PovertyScale',
      version='2021.1.3',
      description=('A docassemble extension.'),
      long_description='# PovertyScale\r\n\r\nPoverty scale, updated approximately on an annual basis, to use for calculating\r\nincome eligibility in the United States.\r\n\r\nSee example and demo in demo_poverty_scale.yml\r\n\r\nThis package contains a JSON file, poverty.json, which can be referenced directly,\r\nas well as a module poverty.py which exports `poverty_scale_income_qualifies`\r\n\r\n```python\r\ndef poverty_scale_income_qualifies(total_monthly_income:float, household_size:int=1, multiplier:int=1)->Union[bool,None]:\r\n  """\r\n  Given monthly income, household size, and an optional multiplier, return whether an individual\r\n  is at or below the federal poverty level.\r\n  \r\n  Returns None if the poverty level data JSON could not be loaded.\r\n  """\r\n  \r\ndef poverty_scale_get_income_limit(household_size:int=1, multiplier:int=1)->Union[int, None]:\r\n  """\r\n  Return the income limit matching the given household size.\r\n  """\r\n  \r\n```',
      long_description_content_type='text/markdown',
      author='Quinten Steenhuis',
      author_email='admin@admin.com',
      license='The MIT License (MIT)',
      url='https://docassemble.org',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=[],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/PovertyScale/', package='docassemble.PovertyScale'),
     )

