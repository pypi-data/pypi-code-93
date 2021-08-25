from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
VERSION = '0.0.9'
setup(
    name='pyiikoapi',
    version=VERSION,
    description='Python services for convenient work with iiko Biz API and iiko Card API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['pyiikoapi','pyiikoapi.biz', 'pyiikoapi.card',],
    # packages=find_packages(where="src"),
    # package_dir={"": "src"},
    author='kebrick',
    author_email='ruban.kebr@gmail.com',
    license='MIT',
    project_urls={
        'Source': 'https://github.com/kebrick/pyiikoapi',
        'Tracker': 'https://github.com/kebrick/pyiikoapi/issues',
    },
    install_requires=['requests',],

    python_requires='>=3',
    zip_safe=False
)
