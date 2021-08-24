from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='v_cloud_market_cli_user',
    version='0.1.2',
    description='V Cloud Market Command Tool For User.',
    long_description=long_description,
    long_description_context_type='text/markdown',
    keywords=['vcloud-market-cli-user'],
    url='https://github.com/virtualeconomy/v-cloud-market-cli-user',
    author='hvoid-build-block',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.5',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python'
    ],
    entry_points={
        'console_scripts': [
            'vcloud = market_place_cli.main_logic:start'
        ]
    },
    install_requires=requirements,
    zip_safe=False,
)