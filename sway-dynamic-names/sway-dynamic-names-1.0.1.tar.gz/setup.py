from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(name='sway-dynamic-names',
      description='Dynamically update the name of each Sway WM workspace using font-awesome icons',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/j-waters/sway-dynamic-workspace-names',
      license='MIT',
      install_requires=["i3ipc", "pyyaml", "fontawesome", "pyxdg", "Click"],
      author='James Waters',
      author_email='james@jcwaters.co.uk',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'sway-dynamic-names=sway_dynamic_names.__main__:main'
          ]
      },
      setup_requires=['setuptools-git-versioning'],
      version_config={
          "template": "{tag}",
          "dev_template": "{tag}.dev{ccount}+git.{sha}",
          "dirty_template": "{tag}.dev{ccount}+git.{sha}.dirty",
          "starting_version": "0.0.1",
          "version_file": "",
          "count_commits_from_version_file": False
      },
      python_requires='>=3.8',
      )
