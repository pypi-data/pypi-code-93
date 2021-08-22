from setuptools import setup

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='vsml',
    version='0.3.1',
    description='a very simple markup language.',
    long_description_content_type="text/markdown",
    long_description=README,
    url='https://github.com/GalaxiaTeam/vsml',
    license='MIT',
    packages=['vsml'],
    author_name='Satyrn',
    author_email='satyrn@tutanota.com',
    keywords=['vsml', 'markup'],
    download_url='https://pypi.org/project/vsml/',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only"
    ],
)

if __name__ == '__main__':
    setup(**setup_args)
